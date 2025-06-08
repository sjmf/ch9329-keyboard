#!/usr/bin/env python
# CH9329 keyboard controller
import signal
import sys
import argparse
import logging

from serial import Serial

from backend.mouse import MouseListener
from backend.keyboard import KeyboardListener

logger = logging.getLogger(__name__)

# Globally visible listener objects for thread stop
ml = None
keeb = None

# Provide different options for handling SIGINT so Ctrl+C can be passed to controller
#  (not that it matters under pyusb, which captures all keyboard output!)
def signal_handler_exit(sig, frame):
    logging.warning('Exiting...')
    stop_threads()
    sys.exit(0)

def signal_handler_ignore(sig, frame):
    logging.debug('Ignoring Ctrl+C')

def stop_threads():
    if isinstance(ml, MouseListener):
        ml.stop()
    
    if isinstance(keeb, KeyboardListener):
        keeb.stop()

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
        help='Set keyboard capture mode',
        default='curses',
        type=str,
        choices=['usb', 'pynput', 'tty', 'curses', 'none'],
    )
    parser.add_argument(
        '--no-keyboard', '-n',
        help='Do not capture keyboard',
        action='store_true'
    )
    parser.add_argument(
        '--mouse', '-e',
        help='Capture mouse input',
        action='store_true'
    )

    return parser.parse_args()

def main():
    args = parse_args()

    # Set log level
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(message)s')

    # Handle SIGINT / Ctrl + C, which user might want to pass through
    if 'exit' in args.sigint:
        signal.signal(signal.SIGINT, signal_handler_exit)
    elif 'ignore' in args.sigint:
        signal.signal(signal.SIGINT, signal_handler_ignore)

    # Set warnings for various options:
    if args.no_keyboard:
        logging.warning("Keyboard input will NOT be passed (--no-keyboard / -n)")
    if args.mode == 'pynput' and args.sigint != 'ignore':
        logging.warning("Consider using --mode='pynput' with --sigint=ignore")
    if args.mode != 'pynput' and args.mouse:
        logging.warning("Ignoring --mode: --mouse (-e) input specified, so will use 'pynput'")
        args.mode = 'pynput'
    # Make serial connection
    serial_port = Serial(args.port, args.baud)

    try:
        # Start mouse listner on --mouse (-e)
        if args.mouse:
            ml = MouseListener(serial_port)
            ml.start()
            # Wait if no keyboard capture
            if args.mode == "none" or args.no_keyboard:
                ml.listener.join()

        # Do not capture keyboard with --no-keyboard (-n)
        if not args.no_keyboard:
            keeb = KeyboardListener(serial_port, mode=args.mode)
            # Run keyboard blocks until completion
            keeb.start()

            keeb.thread.join()

    except KeyboardInterrupt:
        logging.warning("... cleaning up!")
    finally:
        stop_threads() # Stop threads (if running)
        logging.info("Exiting. Bye!")

if __name__ == '__main__':
    main()