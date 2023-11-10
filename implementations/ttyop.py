# tty implementation
import sys
import tty
import termios

import logging
from utils.communication import DataComm
from utils.utils import ascii_to_scancode

logger = logging.getLogger(__name__)


def main_tty(serial_port):
    """
    Main method for control using tty (can run as local user)
    This mode may be useful as a fallback if keyboard detection fails.

    TTY operation mode is a very basic mode which can support pasted text, but
    has no support for modifier keys, which will be parsed by the host and NOT
    passed through to the CH9329 HID keyboard
    """
    logging.info(
        "Using tty operation mode.\n"
        "Paste supported. Modifier keys not supported.\n"
        "Ctrl+C will exit. Console must be focused to input."
    )

    try:
        hid_serial_out = DataComm(serial_port)
        tty.setcbreak(sys.stdin)
        while True:
            ascii_val = sys.stdin.read(1)
            scancode = ascii_to_scancode(ascii_val)
            print(ascii_val, end="", flush=True)
            logging.debug(scancode)

            hid_serial_out.send_scancode(scancode)
            hid_serial_out.release()
    except termios.error as e:
        raise Exception("Run this app from a terminal!") from e
