import threading
from serial import Serial
from enum import Enum

class Mode(Enum):
    NONE   = 0
    USB    = 1
    PYNPUT = 2
    TTY    = 3
    CURSES = 4

class KeyboardListener:
    def __init__(self, serial_port: Serial,  mode: Mode | str = "pynput"):
        self.serial_port = serial_port

        if isinstance(mode, str):
            self.mode = Mode[mode.upper()]
        elif isinstance(mode, Mode):
            self.mode = mode
            
        self.running = False
        self.thread = threading.Thread(target=self.run_keyboard)

    def run(self):
        self.thread.start()
        self.thread.join()

    def start(self):
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
    
    def run_keyboard(self):
        # Select operation mode
        if self.mode is Mode.NONE:
            pass # noop
        elif self.mode is Mode.USB:
            from backend.pyusb import main_usb
            main_usb(self.serial_port)
        elif self.mode is Mode.PYNPUT:
            from backend.pynput import main_pynput
            main_pynput(self.serial_port)
        elif self.mode is Mode.TTY:
            from backend.ttyop import main_tty
            main_tty(self.serial_port)
        elif self.mode is Mode.CURSES:
            from backend.cursesop import main_curses
            main_curses(self.serial_port)
        else:
            raise Exception("Selected mode somehow invalid")
