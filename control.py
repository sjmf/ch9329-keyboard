#!/usr/bin/env python
# CH9329 keyboard controller
import signal
import sys
import argparse
import logging
from implementations.mouse import MouseListener

from serial import Serial

logger = logging.getLogger(__name__)

# Globally visible mouse listener for thread stop
ml = None

# Provide different options for handling SIGINT so Ctrl+C can be passed to controller
#  (not that it matters under pyusb, which captures all keyboard output!)
def signal_handler_exit(sig, frame):
    logging.warning('Exiting...')
    stop_mouse()
    sys.exit(0)

def signal_handler_ignore(sig, frame):
    logging.debug('Ignoring Ctrl+C')

def stop_mouse():
    if isinstance(ml, MouseListener):
        ml.stop()

def parse_args():
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
        default='nohandle',
        type=str,
        choices=['exit', 'ignore', 'nohandle']
    )
    parser.add_argument(
        '--mode', '-m',
        help='Set key capture mode',
        default='curses',
        type=str,
        choices=['usb', 'pynput', 'tty', 'curses'],
    )
    parser.add_argument(
        '--mouse', '-e',
        help='Capture mouse input',
        action='store_true'
    )

    return parser.parse_args()

def run_keyboard(mode, sigint):
    # Select operation mode
    if 'usb' in mode:
        from implementations.pyusb import main_usb
        main_usb(serial_port)
    elif 'pynput' in mode:
        from implementations.pynput import main_pynput
        if 'ignore' not in sigint:
            logging.warning("Consider using pynput mode with --sigint=ignore")
        main_pynput(serial_port)
    elif 'tty' in mode:
        from implementations.ttyop import main_tty
        main_tty(serial_port)
    elif 'curses' in mode:
        from implementations.cursesop import main_curses
        main_curses(serial_port)
    else:
        raise Exception("Selected mode invalid")

if __name__ == '__main__':
    args = parse_args()

    # Set log level
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(message)s')

    # Handle SIGINT / Ctrl + C, which user might want to pass through
    if 'exit' in args.sigint:
        signal.signal(signal.SIGINT, signal_handler_exit)
    elif 'ignore' in args.sigint:
        signal.signal(signal.SIGINT, signal_handler_ignore)

    # Make serial connection
    serial_port = Serial(args.port, args.baud)

    try:
        # Start mouse listner on --mouse
        if args.mouse:
            ml = MouseListener(serial_port)
            ml.start()
        
        # Run keyboard blocks until completion
        run_keyboard(args.mode, args.sigint)
        stop_mouse() # Stop mouse thread (if running)

    except KeyboardInterrupt:
        logging.warning("... cleaning up!")
