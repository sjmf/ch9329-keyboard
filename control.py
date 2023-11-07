#!/usr/bin/env python
# CH9329 keyboard controller
import signal
import sys
import argparse
import logging

from serial import Serial

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


if __name__ == '__main__':
    # Parse arguments using argparse module. Example call:
    # python control.py /dev/cu.usbserial --verbose --mode usb
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
            from implementations.pyusb import main_usb
            main_usb(serial_port)
        case 'pynput':
            from implementations.pynput import main_pynput
            main_pynput(serial_port)
        case 'tty':
            from implementations.ttyop import main_tty
            main_tty(serial_port)
        case 'curses':
            pass
        case _:
            raise Exception("Selected mode invalid")
