# curses implementation
import curses
import logging
import time

from utils.utils import ascii_to_scancode, build_scancode, scancode_to_ascii
from .baseop import KeyboardOp

logger = logging.getLogger(__name__)

MODIFIER_CODES = {
    "KEY_RESIZE": 0x0,
    "KEY_UP": 0x52,
    "KEY_DOWN": 0x51,
    "KEY_LEFT": 0x50,
    "KEY_RIGHT": 0x4F,
    "KEY_NPAGE": 0x4E,
    "KEY_PPAGE": 0x4B,
    "KEY_DC": 0x2A,
    "KEY_BACKSPACE": 0x2A,
    "KEY_HOME": 0x4A,
    "KEY_END": 0x4D,
    "KEY_F(1)": 0x3B,
    "KEY_F(2)": 0x3C,
    "KEY_F(3)": 0x3D,
    "KEY_F(4)": 0x3E,
    "KEY_F(5)": 0x3F,
    "KEY_F(6)": 0x40,
    "KEY_F(7)": 0x41,
    "KEY_F(8)": 0x42,
    "KEY_F(9)": 0x43,
    "KEY_F(10)": 0x44,
    "KEY_F(11)": 0x57,
    "KEY_F(12)": 0x58,
}

# Mapping of control character codes (from curses) to character codes
CONTROL_CHARACTERS = {
    0x11: 0x14,  # ^Q
    0x17: 0x1A,  # ^W
    0x05: 0x08,  # ^E
    0x12: 0x15,  # ^R
    0x14: 0x17,  # ^T
    0x19: 0x1C,  # ^Y
    0x15: 0x18,  # ^U
    0x0F: 0x12,  # ^O
    0x10: 0x13,  # ^P
    0x01: 0x04,  # ^A
    0x13: 0x16,  # ^S
    0x04: 0x07,  # ^D
    0x06: 0x09,  # ^F
    0x07: 0x0A,  # ^G
    0x0B: 0x0E,  # ^K
    0x0C: 0x0F,  # ^L
    0x1A: 0x1D,  # ^Z
    0x18: 0x1B,  # ^X
    0x03: 0x06,  # ^C
    0x16: 0x19,  # ^V
    0x02: 0x05,  # ^B
    0x0E: 0x11,  # ^N
    0x1B: 0x29,  # ^[ Ctrl+ESC
    0x1C: 0x21,  # ^\ Ctrl+4
    0x1D: 0x22,  # ^] Ctrl+5
    0x1E: 0x23,  # ^^ Ctrl+6
    0x1F: 0x24,  # ^_ Ctrl+7
    0x7F: 0x2A,  # ^? Ctrl+8 (also backspace!)
}


class CursesOp(KeyboardOp):
    @property
    def name(self):
        return "curses"

    def run(self):
        # Run curses
        curses.wrapper(self._input_loop)

    def _input_loop(self, term):
        """
        Input loop used by the curses_wrapper function
        Starting point: https://stackoverflow.com/a/32386410/1681205
        :param term:
        """
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

        sc = None
        while True:
            # Keep as much of the code inside this try block as possible!
            # It handles the KeyboardInterrupt raised by Ctrl+C which could come at any time
            try:
                if sc:
                    if logging.DEBUG >= logging.root.level:
                        term.addstr(f"{str(sc)}\t({', '.join([hex(i) for i in sc])})\n")

                    self.hid_serial_out.send_scancode(bytes(sc))
                    sc = None

                try:
                    key = term.getkey()

                    # Is it a 'named key'?
                    if len(key) > 1:
                        # Handle named keys
                        sc = build_scancode(MODIFIER_CODES[key])
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
                    elif ord(key) in CONTROL_CHARACTERS.keys():
                        sc = build_scancode(CONTROL_CHARACTERS[ord(key)], 0x1)

                    # Otherwise, received key was a single character
                    else:
                        sc = ascii_to_scancode(key)

                    if logging.DEBUG >= logging.root.level:
                        term.addstr(str(key) + f"\t{str(hex(ord(key)))}\n")
                    else:
                        term.addstr(str(key))

                    # Handle ESC
                    if ord(key) == 0x1B:
                        break

                except curses.error as e:
                    if "no input" in str(e).lower():
                        time.sleep(0.1)
                        self.hid_serial_out.release()
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
                term.addstr("^C")
                sc = build_scancode(ascii_to_scancode("c")[2], 0x1)

            except curses.error as e:
                term.clear()
                print(e, end="")


def main_curses(serial_port):
    return CursesOp(serial_port).run()
