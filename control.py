#!/usr/bin/env python
# CH9329 keyboard controller
import signal
import sys
import argparse
import logging

from serial import Serial

from pyusb_impl import main_usb

logger = logging.getLogger(__name__)

# TODO: Take parameter from args
stopflag = 0

# Todo: Other methods of capture https://stackoverflow.com/questions/24072790/how-to-detect-key-presses


# Handle Ctrl+C
def signal_handler(sig, frame):
    global stopflag
    logging.warning('Exiting...')
    stopflag = 1

    sys.exit(0)
    # TODO: Handle different signal so Ctrl+C can be passed to controller
    #       (not that it matters under pyusb, which captures all keyboard output!)




def main_pynput():
    from pynput.keyboard import Key, Listener

    def on_press(key):
        print('{0} pressed'.format(key))

    def on_release(key):
        print('{0} release'.format(key))
        if key == Key.esc:
            # Stop listener
            return False

    # Collect events until released
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def main_tty():
    import tty
    import termios

    # The below may be useful as a fallback if keyboard detection fails:
    try:
        tty.setcbreak(sys.stdin)
        while True:
            ascii_val = sys.stdin.read(1)
            print(hex(ord(ascii_val) - 0x5D))
    except termios.error as e:
        raise Exception("Run this app from a terminal!") from e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='CH9329 Control Script',
        description='Use a serial terminal as a USB keyboard!',
        epilog='(c) 2023 Samantha Finnigan. MIT License',
    )

    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('port', action='store')
    parser.add_argument(
        '--mode', '-m',
        help='Set key capture mode',
        default='usb',
        type=str,
        choices=['usb', 'pynput', 'tty', 'curses'],
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(message)s')

    signal.signal(signal.SIGINT, signal_handler)

    serial_port = Serial(args.port, 9600)

    # Python >3.10 required to use case statement:
    match args.mode:
        case 'usb':
            main_usb(serial_port)
        case 'pynput':
            main_pynput(serial_port)
        case 'tty':
            main_tty(serial_port)
        case 'curses':
            pass
        case _:
            raise Exception("Selected mode invalid")
