# curses implementation
import curses
import logging
import time

from utils.communication import DataComm
from utils.utils import ascii_to_scancode, build_scancode, scancode_to_ascii

logger = logging.getLogger(__name__)

port = None

keys_with_codes = {
    'KEY_RESIZE': 0x0,
    'KEY_UP': 0x52, 'KEY_DOWN': 0x51, 'KEY_LEFT': 0x50, 'KEY_RIGHT': 0x4f,
    'KEY_NPAGE': 0x4e, 'KEY_PPAGE': 0x4b, 'KEY_DC': 0x2a, 'KEY_BACKSPACE': 0x2a,
    'KEY_HOME': 0x4a, 'KEY_END': 0x4d,
    'KEY_F(1)': 0x3b, 'KEY_F(2)': 0x3c, 'KEY_F(3)': 0x3d, 'KEY_F(4)': 0x3e,
    'KEY_F(5)': 0x3f, 'KEY_F(6)': 0x40, 'KEY_F(7)': 0x41, 'KEY_F(8)': 0x42,
    'KEY_F(9)': 0x43, 'KEY_F(10)': 0x44, 'KEY_F(11)': 0x57, 'KEY_F(12)': 0x58,
}

# Mapping of control character codes (from curses) to character codes
control_characters = {
    0x11: 0x14,  # ^Q
    0x17: 0x1A,  # ^W
    0x05: 0x08,  # ^E
    0x12: 0x15,  # ^R
    0x14: 0x17,  # ^T
    0x19: 0x1C,  # ^Y
    0x15: 0x18,  # ^U
    0x0f: 0x12,  # ^O
    0x10: 0x13,  # ^P
    0x01: 0x04,  # ^A
    0x13: 0x16,  # ^S
    0x04: 0x07,  # ^D
    0x06: 0x09,  # ^F
    0x07: 0x0a,  # ^G
    0x0b: 0x0e,  # ^K
    0x0c: 0x0f,  # ^L
    0x1a: 0x1d,  # ^Z
    0x18: 0x1b,  # ^X
    0x03: 0x06,  # ^C
    0x16: 0x19,  # ^V
    0x02: 0x05,  # ^B
    0x0e: 0x11,  # ^N
    0x1b: 0x29,  # ^[ Ctrl+ESC
    0x1c: 0x21,  # ^\ Ctrl+4
    0x1d: 0x22,  # ^] Ctrl+5
    0x1e: 0x23,  # ^^ Ctrl+6
    0x1f: 0x24,  # ^_ Ctrl+7
    0x7f: 0x2a,  # ^? Ctrl+8 (also backspace!)
}


def input_loop(term):
    """
    Input loop used by the curses_wrapper function
    :param term:
    """
    global port
    curses.raw()
    term.nodelay(True)
    term.clear()
    term.keypad(True)

    term.addstr(
        "Using curses operation mode.\n"
        "Can run as standard user.\n"
        "Paste supported. *SOME* modifier keys supported.\n"
        "Input requires terminal focus.\n"
        "Press ESC to exit.\n"
    )

    # Establish class for communication
    hid_serial_out = DataComm(port)

    sc = None
    while True:
        # Keep as much of the code inside this try block as possible!
        # It handles the KeyboardInterrupt raised by Ctrl+C which could come at any time
        try:
            if sc:
                if logging.DEBUG >= logging.root.level:
                    term.addstr(f"{str(sc)}\t({', '.join([hex(i) for i in sc])})\n")

                hid_serial_out.send_scancode(sc)
                sc = None

            try:
                key = term.getkey()

                # Is it a 'named key'?
                if len(key) > 1:
                    # Handle named keys
                    sc = build_scancode(keys_with_codes[key])
                    ascii_rep = scancode_to_ascii(sc)
                    if ascii_rep:
                        if logging.DEBUG >= logging.root.level:
                            term.addstr(ascii_rep + f"\t{str(hex(sc[2]))}\n")
                        else:
                            term.addstr(ascii_rep)
                        continue

                    term.addstr(key)
                    continue

                # Is it a control character?
                elif ord(key) in control_characters.keys():
                    sc = build_scancode(control_characters[ord(key)], 0x1)

                # Otherwise, received key was a single character
                else:
                    sc = ascii_to_scancode(key)

                if logging.DEBUG >= logging.root.level:
                    term.addstr(str(key) + f"\t{str(hex(ord(key)))}\n")
                else:
                    term.addstr(str(key))

                # Handle ESC
                if ord(key) == 0x1b:
                    break

            except curses.error as e:
                if "no input" in str(e).lower():
                    time.sleep(.1)
                    hid_serial_out.release()
                    continue
                elif "addwstr" in str(e).lower():
                    term.clear()
                    continue
                # Otherwise, log the error.
                term.addstr(e)

            except KeyError as e:
                term.addstr(str(e) + "\tOrdinal missing\n")

            except ValueError as e:
                term.addstr(str(e) + "\n")

        except KeyboardInterrupt as e:
            term.addstr('^C')
            sc = build_scancode(ascii_to_scancode('c')[2], 0x1)

        except curses.error as e:
            term.clear()
            print(e, end='')


def main_curses(serial_port):
    """
    Main method for curses implementation
    Starting point: https://stackoverflow.com/a/32386410/1681205
    :param serial_port:
    :return:
    """
    global port
    port = serial_port
    curses.wrapper(input_loop)
