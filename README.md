# CH9329 KVM Controller

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)

__PLEASE NOTE: I am a hobbyist. I have no affiliation with any manufacturer developing or selling CH9329 hardware.__

A software KVM script using the CH9329 UART Serial to USB HID controller, in Python.

This script can transmit keyboard and mouse input over a UART serial connection to a second device, using a CH9329 module. You can find these from vendors on eBay and AliExpress for next to nothing. However, there is very little software support available for these modules, and protocol documentation is sparse.

This Python script includes several methods to capture keyboard scan codes from a keyboard attached to the local computer where the script is running, and send them via Serial UART to the device which the USB HID keyboard is listening on. For most purposes, the default 'curses' mode will suffice.

Mouse capture is provided using the parameter `--mouse`. It uses pynput for capturing mouse input and transmits this over the serial link simultaneously to keyboard input. Appropriate system permissions (Privacy and Security) may be required to use mouse capture.

## Usage

Packages from `requirements.txt` must be installed first. Use your preferred python package manager. E.g.:

```bash
# Conda
conda create -n kvm
conda activate kvm
# OR Venv (don't use both!)
python -m venv ./.venv
./.venv/scripts/activate
# Then, use pip to install dependencies
pip install -r requirements.txt
```

Usage examples for the `control.py` script:

```bash
# Use default mode; enable mouse support; use a Mac OSX serial port:
python control.py --mouse /dev/cu.usbserial-A6023LNH
# Run the script using keyboard 'tty' mode
python control.py --mode tty /dev/tty.usbserial0
# Run using `pyusb` keyboard mode (which requires root):
sudo python control.py --mode usb /dev/tty.usbserial0
# Increase verbosity using --verbose (or -v), and use COM1 serial port (Windows)
python control.py --verbose COM1
```

Use `python control.py --help` to view all available options.

## Keyboard capture mode comparison

Some capture methods require superuser privileges (`sudo`), for example `pyusb` provides the most accurate keyboard scancode capture, but needs to de-register the device driver for the input method in order to control it directly.

For example usage, please see the accompanying blogpost: https://wp.finnigan.dev/?p=682

| Mode     | Modifiers  | Paste  | Blocking   | Focus  | Exit     | Permissions            |
|----------|------------|--------|------------|--------|----------|------------------------|
| `usb`    | ✅ Yes     | ❌ No  | ✅ Yes      | ❌ No  | Ctrl+ESC | `sudo` / root          |
| `tty`    | ❌ No      | ✅ Yes | ❌ No       | ✅ Yes | Ctrl+C   | Standard user          |
| `pynput` | ✅ Yes     | ❌ No  | ❌ No       | ❌ No  | Ctrl+ESC | Input monitoring (OSX) |
| `curses` | ⚠️ Some    | ✅ Yes | ❌ No       | ✅ Yes | ESC      | Standard user          |

For `curses`, modifier support is incomplete but should be good enough to enable working in a terminal. Curses provides a good mix of functionality versus permissions and is therefore the default mode.

A 'yes' in the remaining columns means:

 * **Modifiers**:
Keys like `Ctrl`, `Shift`, `Alt` and `Cmd`/`Win` will be captured. Combinations like Ctrl+C will be passed through.
 * **Paste**: 
Content can be pasted into the console and will be transmitted char-wise to the HID device
 * **Blocking**:
Keyboard input will not function in other applications while the script is running
 * **Focus**:
The console must remain in focus for input to be recorded (and transmitted over the UART)
 * **Implication**:
You will need to select the best input method for your use case! 

## Troubleshooting

**Permissions errors on Linux**: if your system user does not have serial write permissions (resulting in a permission error), you can add your user to the `dialout` group: e.g. `sudo usermod -a -G dialout $USER`. You must fully log out of the system to apply the change.

**Difficulty installing requirements**: If you get `command not found: pip` or similar when installing requirements, try: `python -m pip [...]` to run pip instead.

## Acknowledgements
With thanks to [@beijixiaohu](https://github.com/beijixiaohu), the original author of the [ch9329Comm PyPi package](https://pypi.org/project/ch9329Comm/) and [GitHub repo](https://github.com/beijixiaohu/CH9329_COMM/) (in Chinese), some code of which is re-used under the MIT License.

## License
(c) 2023-25 Samantha Finnigan (except where acknowledged) and released under [MIT License](LICENSE.md).

