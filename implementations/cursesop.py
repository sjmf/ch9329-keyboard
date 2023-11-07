# curses implementation
import curses
import logging
import time

from communication import DataComm
from util import ascii_to_scancode, build_scancode, scancode_to_ascii

logger = logging.getLogger(__name__)

port = None

keys_with_codes = {
    'KEY_RESIZE': 0x0,
    'KEY_UP': 0x52, 'KEY_DOWN': 0x51, 'KEY_LEFT': 0x50, 'KEY_RIGHT': 0x4f,
    'KEY_NPAGE': 0x4e, 'KEY_PPAGE': 0x4b, 'KEY_DC': 0x2a, 'KEY_BACKSPACE': 0x2a,
    'KEY_HOME': 0x4a, 'KEY_END': 0x4d,
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
        "Input will continue in background without terminal focus.\n"
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
                    term.addstr('\n' + str(sc))

                hid_serial_out.send_scancode(sc)
                sc = None

            try:
                key = term.getkey()

                if len(key) > 1:
                    # Handle named keys
                    sc = build_scancode(keys_with_codes[key])
                    ascii_rep = scancode_to_ascii(sc)
                    if ascii_rep:
                        if logging.DEBUG >= logging.root.level:
                            term.addstr(ascii_rep + '\t' + str(hex(sc[2])) + "\n")
                        else:
                            term.addstr(ascii_rep)
                        continue

                    term.addstr(key)
                    continue

                # Otherwise, received key was a single character
                sc = ascii_to_scancode(key)

                if logging.DEBUG >= logging.root.level:
                    term.addstr(str(key) + '\t' + str(hex(ord(key))) + "\n")
                else:
                    term.addstr(str(key))

                # Handle ESC
                if ord(key) == 0x1b:
                    break

            except curses.error as e:
                if "no input" in str(e).lower():
                    time.sleep(.1)
                    continue
                elif "addwstr" in str(e).lower():
                    term.clear()
                    continue
                # Otherwise, log the error.
                term.addstr(e)

            except KeyError as e:
                term.addstr(str(e) + '\t' + "Ordinal missing\n")

        except KeyboardInterrupt as e:
            term.addstr('^C')
            sc = build_scancode(ascii_to_scancode('c')[2], 0x1)

        except curses.error as e:
            term.clear()
            print(e, end='')


        # if key == os.linesep:
        #     break


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
