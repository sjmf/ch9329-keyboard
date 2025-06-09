#!/usr/bin/env python
import sys
import os
import subprocess
import logging
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox

from utils.communication import list_serial_ports

logger = logging.getLogger(__name__)
    
class KVMGui(tk.Tk):

    """
    A graphical user interface (GUI) for controlling a CH9329-based software KVM (Keyboard, Video, Mouse) switch.
    This class provides a Tkinter-based window that allows users to select various options for keyboard, video, and mouse control,
    configure serial port settings, and start or stop the KVM functionalities. It supports different keyboard backends, serial port selection,
    baud rate configuration, and toggling of windowed mode and verbose logging.

    Attributes:
        kb_backends (list): Available keyboard backend options.
        serial_ports (list): List of detected serial ports.
        baud_rates (list): Supported baud rates for serial communication.
        keyboard_var (tk.BooleanVar): State of the keyboard checkbox.
        video_var (tk.BooleanVar): State of the video checkbox.
        mouse_var (tk.BooleanVar): State of the mouse checkbox.
        kb_backend_var (tk.StringVar): Selected keyboard backend.
        serial_port_var (tk.StringVar): Selected serial port.
        baud_rate_var (tk.IntVar): Selected baud rate.
        window_var (tk.BooleanVar): State of the windowed mode checkbox.
        verbose_var (tk.BooleanVar): State of the verbose logging checkbox.
        process (subprocess.Popen): Handle of the subprocess launched
    Methods:
        __init__():
            Initializes the KVMGui window, widgets, and variables.
        on_start():
            Handles the logic for starting the KVM functionalities based on user selections.
            Sets up logging, establishes serial connection, and starts selected listeners or capture devices.
        stop_threads():
            Stops and cleans up any running listener or capture device threads.
        on_exit():
            Stops all running threads and closes the GUI window.
    """

    kb_backends: list[str]
    serial_ports: list[str]
    baud_rates: list[int]
    keyboard_var: tk.BooleanVar
    video_var: tk.BooleanVar
    mouse_var: tk.BooleanVar
    kb_backend_var: tk.StringVar
    serial_port_var: tk.StringVar
    baud_rate_var: tk.IntVar
    window_var: tk.BooleanVar
    verbose_var: tk.BooleanVar
    process: subprocess.Popen | None

    def __init__(self) -> None:
        super().__init__()

        TYPEFACE = tkfont.nametofont("TkDefaultFont").actual("family")

        # Dropdown values
        self.kb_backends = ["pynput", "curses", "tty", "usb"]
        self.serial_ports = list_serial_ports()
        self.baud_rates = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]

        if len(self.serial_ports) == 0:
            self.destroy()
            messagebox.showerror("Start-up Error!", "No serial ports found. Exiting.")
            return
        
        # Window characteristics
        self.title("Python KVM")
        self.resizable(False, False)

        # Checkboxes
        self.keyboard_var = tk.BooleanVar(value=True)
        self.video_var = tk.BooleanVar(value=True)
        self.mouse_var = tk.BooleanVar(value=True)
        self.kb_backend_var = tk.StringVar(value=self.kb_backends[0])
        self.serial_port_var = tk.StringVar(value=self.serial_ports[-1])
        self.baud_rate_var = tk.IntVar(value=self.baud_rates[3])
        self.window_var = tk.BooleanVar(value=False)
        self.verbose_var = tk.BooleanVar(value=False)

        # Title row
        tk.Label(self, text="KVM Controller", font=(TYPEFACE, 14, "bold")).grid(row=0, column=0, padx=(10, 10), pady=(10, 10))
        
        # Vertical bar between columns 0 and 1, spanning rows 1-3
        bar = tk.Frame(self, width=1, height=100, bg="gray")
        bar.grid(row=1, column=0, rowspan=3, sticky="ne", padx=(0, 10), pady=(10, 0))

        # Checkboxes
        tk.Checkbutton(self, text="Keyboard", variable=self.keyboard_var).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tk.Checkbutton(self, text="Video", variable=self.video_var).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        tk.Checkbutton(self, text="Mouse", variable=self.mouse_var).grid(row=3, column=0, sticky="w", padx=10, pady=5)

        tk.Checkbutton(self, text="Windowed", variable=self.window_var).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        tk.Checkbutton(self, text="Verbose Logging (term)", variable=self.verbose_var).grid(row=0, column=2, sticky="w", padx=10, pady=5)

        # Keyboard backend dropdown
        tk.Label(self, text="Keyboard backend").grid(row=1, column=1, sticky="w", padx=10)
        ttk.Combobox(self, textvariable=self.kb_backend_var, values=self.kb_backends, state="readonly").grid(row=1, column=2, padx=10, pady=5)

        # Serial port dropdown
        tk.Label(self, text="Serial Port").grid(row=2, column=1, sticky="w", padx=10)
        ttk.Combobox(self, textvariable=self.serial_port_var, values=self.serial_ports).grid(row=2, column=2, padx=10, pady=5)

        # Baud rate dropdown
        tk.Label(self, text="Baud rate").grid(row=3, column=1, sticky="w", padx=10)
        ttk.Combobox(self, textvariable=self.baud_rate_var, values=[str(rate) for rate in self.baud_rates], state="readonly").grid(row=3, column=2, padx=10, pady=5)

        # Start and Exit buttons
        tk.Button(self, text="Start", width=15, command=self.on_start).grid(row=4, column=1, pady=20, padx=(0, 5))
        tk.Button(self, text="Exit", width=15, command=self.on_exit).grid(row=4, column=2, pady=20, padx=(5, 10))

        # Footer row
        footer = tk.Label(self, text="To exit, press Ctrl + ESC", font=(TYPEFACE, 11), fg="gray")
        footer.grid(row=5, column=0, columnspan=3, pady=(0, 20))

        logging.debug("Initialised Window")

    def on_start(self) -> None:
        # Launch KVM
        logging.info(
            f"""
            Starting Software KVM with parameters:
                Serial port:      {self.serial_port_var.get()} 
                Baud rate:        {self.baud_rate_var.get()}
                Keyboard backend: {self.kb_backend_var.get()}
                Keyboard:         {self.keyboard_var.get()}
                Video:            {self.video_var.get()}
                Mouse:            {self.mouse_var.get()}
                Windowed:         {self.window_var.get()}
                Verbose:          {self.verbose_var.get()}
            """
        )

        try:
            # Enormous threading issues. Need to call ./control.py as a subprocess 
            # This is a workaround for crash:
            # [1] 47591 illegal hardware instruction ... python kvm.py
            env = os.environ.copy()
            env["PYTHONPATH"] = "."

            args = [
                sys.executable,
                os.path.join(os.path.dirname(__file__), 'control.py'),
                str(self.serial_port_var.get()),
                '--baud', str(self.baud_rate_var.get()),
                '--mode', str(self.kb_backend_var.get())
            ]
            if self.video_var.get():
                args.append('--video')
            if self.window_var.get():
                args.append('--windowed')
            if self.mouse_var.get():
                args.append('--mouse')
            if self.verbose_var.get():
                args.append('--verbose')
            if not self.keyboard_var.get():
                args.append('--no-keyboard')

            logging.debug(f"Subprocess args: {args}")
            self.process = subprocess.Popen(args, env=env)

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
            self.on_exit()
        finally:
            logging.info("Done launching KVM")

    def stop_subprocess(self) -> None:
        # Terminate the control.py subprocess if it exists
        if hasattr(self, 'process') and self.process is not None:
            try:
                logging.info("Stopping control.py subprocess")
                self.process.terminate()
                self.process.wait(timeout=2)  # Wait up to 2 seconds for subprocess to exit
            except subprocess.TimeoutExpired:
                logging.warning("Subprocess did not exit in time, killing it.")
                self.process.kill()
                self.process.wait()
            except Exception as e:
                logging.error(f"Failed to terminate control.py subprocess: {e}")
            self.process = None

    def on_exit(self) -> None:
        self.stop_subprocess()
        self.destroy()

def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    app = KVMGui()
    app.mainloop()

if __name__ == "__main__":
    main()