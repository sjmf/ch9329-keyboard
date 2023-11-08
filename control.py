#!/usr/bin/env python
# CH9329 keyboard controller
import signal
import sys
import argparse
import logging

from serial import Serial

logger = logging.getLogger(__name__)


# Provide different options for handling SIGINT so Ctrl+C can be passed to controller
#  (not that it matters under pyusb, which captures all keyboard output!)
def signal_handler_exit(sig, frame):
    logging.warning('Exiting...')
    sys.exit(0)


def signal_handler_ignore(sig, frame):
    logging.debug('Ignoring Ctrl+C')


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
        '-b', '--baud',
        help='Set baud rate for serial device',
        default=9600,
        type=int
    )
    parser.add_argument(
        '-s', '--sigint',
        help="Capture SIGINT (Ctrl+C) instead of handling in shell",
        action='store',
        type=str,
        default='nohandle',
        choices=['exit', 'ignore', 'nohandle']
    )
    parser.add_argument(
        '--mode', '-m',
        help='Set key capture mode',
        default='usb',
        type=str,
        choices=['usb', 'pynput', 'tty', 'curses'],
    )

    args = parser.parse_args()

    # Set log level
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(message)s')

    # Handle SIGINT / Ctrl + C, which user might want to pass through
    if 'exit' in args.sigint:
        signal.signal(signal.SIGINT, signal_handler_ignore)
    elif 'ignore' in args.sigint:
        signal.signal(signal.SIGINT, signal_handler_exit)

    serial_port = Serial(args.port, args.baud)

    # Select operation mode
    if 'usb' in args.mode:
        from implementations.pyusb import main_usb
        main_usb(serial_port)
    elif 'pynput' in args.mode:
        from implementations.pynput import main_pynput
        main_pynput(serial_port)
    elif 'tty' in args.mode:
        from implementations.ttyop import main_tty
        main_tty(serial_port)
    elif 'curses' in args.mode:
        from implementations.cursesop import main_curses
        main_curses(serial_port)
    else:
        raise Exception("Selected mode invalid")
