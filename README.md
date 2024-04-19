# CH9329 keyboard controller script

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)

__PLEASE NOTE: I am a hobbyist. I have no affiliation with any manufacturer developing or selling CH9329 hardware.__

A script to send keyboard commands over a UART serial connection to a CH9329 UART Serial to USB HID keyboard controller. You can find these from vendors on eBay and AliExpress for next to nothing. However, there is very little software support available for these modules and the protocol documentation is written in Chinese.

This Python script includes several methods to capture keyboard scan codes from a keyboard attached to the local computer where the script is running, and send them via Serial UART to the device which the USB HID keyboard is listening on.

Some capture methods require superuser privileges (`sudo`), for example `pyusb` provides the most accurate keyboard scancode capture, but needs to de-register the device driver for the input method in order to control it directly.

## Usage

Packages from `requirements.txt` must be installed first. Use your preferred python package manager.

```bash
python control.py --mode tty
# or
sudo python control.py --mode usb
# increase verbosity using --verbose (or -v)
python control.py --verbose
```

Use `python control.py --help` to view all available options.

The operation of the `mode` parameter is described below.

## Keyboard capture mode comparison

| Mode   | Modifiers  | Paste  | Blocking   | Focus  | Exit     | Permissions            |
|--------|------------|--------|------------|--------|----------|------------------------|
| `usb`    | ✅ Yes     | ❌ No  | ✅ Yes      | ❌ No  | Ctrl+ESC | `sudo` / root          |
| `tty`    | ❌ No      | ✅ Yes | ❌ No       | ✅ Yes | Ctrl+C   | Standard user          |
| `pynput` | ✅ Yes     | ❌ No  | ❌ No       | ❌ No  | Ctrl+ESC | Input monitoring (OSX) |
| `curses` | ⚠️ Some    | ✅ Yes | ❌ No       | ✅ Yes | ESC      | Standard user          |

A 'yes' in one of the above columns means:

#### Modifiers
Keys like `Ctrl`, `Shift`, `Alt` and `Cmd` (or `super` or `Win`, if you prefer) will be captured.
This means that combinations like Ctrl+C will be passed through.

For `curses`, support is incomplete, but should be complete enough to enable working in a terminal.

#### Paste
Content can be pasted into the console and will be transmitted char-wise to the HID device

#### Blocking
Keyboard input will not function in other applications while the script is running

#### Focus
The console must remain in focus for input to be recorded (and transmitted over the UART)

### Implication

This means that you will need to select the best input method for your use case! 

## Acknowledgements
With thanks to the original author of the [ch9329Comm PyPi package](https://pypi.org/project/ch9329Comm/) (in Chinese), some code of which is re-used under the MIT License.

## License
(c) 2023 Samantha Finnigan (except where acknowledged) and released under [MIT License](LICENSE.md).

