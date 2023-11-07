# pynput implementation
import logging

from pynput.keyboard import Key, KeyCode, Listener

from communication import DataComm
from util import ascii_to_scancode, merge_scancodes

logger = logging.getLogger(__name__)

modifier_to_value = {
    Key.alt: 0x04, Key.alt_l: 0x04, Key.alt_r: 0x40, Key.alt_gr: 0x40,
    Key.shift: 0x02, Key.shift_l: 0x02, Key.shift_r: 0x20,
    Key.cmd: 0x08, Key.cmd_l: 0x08, Key.cmd_r: 0x80,
    Key.ctrl: 0x01, Key.ctrl_l: 0x01, Key.ctrl_r: 0x10,
}

keys_with_codes = {
    Key.up: 0x52, Key.down: 0x51, Key.left: 0x50, Key.right: 0x4f,
    Key.delete: 0x4c, Key.backspace: 0x2a,
    Key.f1: None, Key.f2: None, Key.f3: None, Key.f4: None,
    Key.f5: None, Key.f6: None, Key.f7: None, Key.f8: None,
    Key.f9: None, Key.f10: None, Key.f11: None, Key.f12: None,
    Key.f13: None, Key.f14: None, Key.f15: None, Key.f16: None,
    Key.f17: None, Key.f18: None, Key.f19: None, Key.f20: None,
    Key.home: 0x4a, Key.end: 0x4d, Key.page_down: 0x4e, Key.page_up: 0x4b,
    Key.space: 0x2C, Key.tab: 0x2B, Key.enter: 0x28,
    Key.caps_lock: 0x39,
    Key.media_play_pause: None, Key.media_volume_mute: None,
    Key.media_volume_down: None, Key.media_volume_up: None,
    Key.media_previous: None, Key.media_next: None,
    Key.esc: 0x29,
}


def main_pynput(serial_port):
    """
    Main method for control using pynput
    :param serial_port:
    :return:
    """
    logging.info(
        "Using pynput operation mode.\n"
        "Can run as standard user, but Accessibility "
        "permission for input capture is required in Mac OSX.\n" 
        "Paste not supported. Modifier keys supported.\n"
        "Input will continue in background without terminal focus.\n"
        "Press Ctrl+ESC or Ctrl+C to exit."
    )

    hid_serial_out = DataComm(serial_port)
    held_keys_map = {}

    def on_press(key):
        if key in held_keys_map:
            return  # Skip it!

        scancode = [b for b in b'\x00' * 8]

        try:
            # Handle modifiers
            if isinstance(key, Key):
                if key in modifier_to_value:
                    value = modifier_to_value[key]
                    scancode[0] = value
                else:
                    value = keys_with_codes[key]
                    scancode[2] = value

            # Handle alphanumerics
            if isinstance(key, KeyCode):
                scancode = ascii_to_scancode(key.char)

            held_keys_map[key] = scancode
        except KeyError as e:
            logging.error("Key not found: " + str(e))

        # Merge keys in the held_keys_map and send over serial
        scancode = merge_scancodes(held_keys_map.values())
        logging.debug(scancode)
        hid_serial_out.send_scancode(scancode)

    def on_release(key):
        try:
            held_keys_map.pop(key)
        except KeyError:
            pass  # That's okay, sometimes input gets lost.

        # Ctrl + ESC escape sequence
        if key == Key.esc and Key.ctrl in held_keys_map:
            # Stop listener
            return False

    # Collect events until released
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
