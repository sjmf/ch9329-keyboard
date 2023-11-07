# PyUSB implementation
import logging

import usb.core
from communication import DataComm

logger = logging.getLogger(__name__)


def main_usb(serial_port):
    """
    Main method for control using pyusb (requires superuser)
    :return:
    """
    logging.info(
        "Using PyUSB operation mode.\n"
        "All modifier keys supported. Paste not supported."
    )

    # Required scope for 'finally' block
    dev = interface_number = None

    try:
        usb_endpoints = get_usb_endpoints()
        endpoint, dev, cfg, intf, interface_number = [*usb_endpoints.values()][0]

        hid_serial_out = DataComm(serial_port)
        debounce = None

        # Detach kernel driver to perform raw IO with device (requires elevated sudo privileges)
        # Otherwise you will receive "[Errno 13] Access denied (insufficient permissions)"
        if dev.is_kernel_driver_active(interface_number):
            dev.detach_kernel_driver(interface_number)

        logging.info("Press Ctrl+ESC to exit")
        while True:
            # Keyboard scancodes
            data_in = endpoint.read(endpoint.wMaxPacketSize, timeout=100)

            # Debug print scancodes:
            logging.debug(
                f"{data_in}, \t"
                f"({', '.join([hex(i) for i in data_in])})\t"
                f"{scancode_to_ascii(data_in)}"
            )

            # Check for escape sequence (and helpful prompt)
            if data_in[0] == 0x1 and data_in[2] == 0x6 and debounce != 'c':  # Ctrl+C:
                logging.warning("\nCtrl+C passed through. Use Ctrl+ESC to exit!")

            if data_in[0] == 0x1 and data_in[2] == 0x29:  # Ctrl+ESC:
                logging.warning("\nCtrl+ESC escape sequence detected! Exiting...")
                break

            key = scancode_to_ascii(data_in)

            if key != debounce and key:
                print(key, end="", flush=True)
                debounce = key
            elif not key:
                debounce = None

            hid_serial_out.send_scancode(data_in)

    except usb.core.USBError as e:
        logging.error(e)

    finally:
        usb.util.dispose_resources(dev)
        dev.attach_kernel_driver(interface_number)


def get_usb_endpoints():
    # Find all USB devices
    devices = usb.core.find(find_all=True)
    endpoints = {}

    # Iterate through connected USB devices
    for device in devices:
        # Check if the device is a keyboard
        if device.bDeviceClass == 0 and device.bDeviceSubClass == 0:
            dev = usb.core.find(idVendor=device.idVendor, idProduct=device.idProduct)

            if dev is None:
                raise ValueError('device not found')

            cfg = dev.get_active_configuration()
            interface_number = cfg[(0, 0)].bInterfaceNumber
            intf = usb.util.find_descriptor(cfg, bInterfaceNumber=interface_number)

            endpoint = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress)
                                       == usb.util.ENDPOINT_IN
                                       and usb.util.endpoint_type(e.bmAttributes)
                                       == usb.util.ENDPOINT_TYPE_INTR,
            )

            if not endpoint:
                continue

            # A keyboard will have the following: (https://wuffs.org/blog/mouse-adventures-part-5)
            # bInterfaceClass == 0x3
            # bInterfaceSubClass == 0x1
            # bInterfaceProtocol == 0x1 (mouse is protocol 0x2)
            if not (
                    intf.bInterfaceClass == 0x3
                    and intf.bInterfaceSubClass == 0x1
                    and intf.bInterfaceProtocol == 0x1
            ):
                continue

            logger.info(
                f"Keyboard: vID: 0x{device.idVendor:04x}; "
                f"pID: 0x{device.idProduct:04x}; "
                f"if: {interface_number}"
            )
            logger.debug(intf)

            endpoints[f"{device.idVendor:04x}:{device.idProduct:04x}"] = (
                endpoint,
                dev,
                cfg,
                intf,
                interface_number,
            )

    return endpoints


def scancode_to_ascii(scancode):
    """
    Convert a keyboard scancode to its ASCII representation
    :param scancode:
    :return:
    """
    key = 0
    index = 2

    # If multiple keydowns come in before a key-up, they are buffered in the rollover buffer
    while index < 8:
        key = scancode[index]
        if key > 0:
            break
        index += 1

    # This function is customised to UK-ISO keyboard layout. ANSI scancodes have differences.
    hid_to_ascii_mapping = {
        0x04: 'a', 0x05: 'b', 0x06: 'c', 0x07: 'd', 0x08: 'e', 0x09: 'f', 0x0a: 'g', 0x0b: 'h',
        0x0c: 'i', 0x0d: 'j', 0x0e: 'k', 0x0f: 'l', 0x10: 'm', 0x11: 'n', 0x12: 'o', 0x13: 'p',
        0x14: 'q', 0x15: 'r', 0x16: 's', 0x17: 't', 0x18: 'u', 0x19: 'v', 0x1a: 'w', 0x1b: 'x',
        0x1c: 'y', 0x1d: 'z',
        0x1E: '1', 0x1F: '2', 0x20: '3', 0x21: '4', 0x22: '5', 0x23: '6', 0x24: '7', 0x25: '8',
        0x26: '9', 0x27: '0', 0x2D: '-', 0x2E: '=',
        0x28: '\n', 0x2C: ' ', 0x2B: '\t', 0x2a: '\b',
        0x2F: '[', 0x30: ']', 0x32: '#', 0x33: ';', 0x34: '\'', 0x35: '`',
        0x36: ',', 0x37: '.', 0x38: '/', 0x39: 'CAPSLOCK', 0x29: 'ESC',
        0x49: 'Ins', 0x4a: 'Home', 0x4b: 'PgUp', 0x4c: 'Del', 0x4d: 'End', 0x4e: 'PgDn',
        0x4f: '→', 0x50: '←', 0x51: '↓', 0x52: '↑',
        0x64: '\\'
    }

    # Overwrite dict values for shift-modified keys. Note: must deep-copy dict!
    modifier_ascii_mapping = hid_to_ascii_mapping.copy()
    modifier_ascii_mapping.update({
        0x04: 'A', 0x05: 'B', 0x06: 'C', 0x07: 'D', 0x08: 'E', 0x09: 'F', 0x0A: 'G', 0x0B: 'H',
        0x0C: 'I', 0x0D: 'J', 0x0E: 'K', 0x0F: 'L', 0x10: 'M', 0x11: 'N', 0x12: 'O', 0x13: 'P',
        0x14: 'Q', 0x15: 'R', 0x16: 'S', 0x17: 'T', 0x18: 'U', 0x19: 'V', 0x1A: 'W', 0x1B: 'X',
        0x1C: 'Y', 0x1D: 'Z',
        0x1E: '!', 0x1F: '"', 0x20: '#', 0x21: '$', 0x22: '%', 0x23: '^', 0x24: '&', 0x25: '*',
        0x26: '(', 0x27: ')', 0x2D: '_', 0x2E: '+',
        0x2F: '{', 0x30: '}', 0x32: '~', 0x33: ':', 0x34: '@', 0x35: '¬',
        0x36: '<', 0x37: '>', 0x38: '?',
        0x64: '|'
    })

    try:
        if scancode[0] & 0x22 or scancode[0] & 0x22:  # LShift 0x2 or RShift 0x20 held
            return modifier_ascii_mapping[key]
        return hid_to_ascii_mapping[key]
    except KeyError as e:
        return None
