# PyUSB implementation
import logging

import usb.core
from utils.communication import DataComm
from utils.utils import scancode_to_ascii

logger = logging.getLogger(__name__)


def main_usb(serial_port):
    """
    Main method for control using pyusb (requires superuser)
    :return:
    """
    logging.info(
        "Using PyUSB operation mode.\n"
        "All modifier keys supported. Paste not supported.\n"
        "Requires superuser permission.\n"
        "Input blocked and collected outside console focus."
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
            # Read keyboard scancodes
            try:
                data_in = endpoint.read(endpoint.wMaxPacketSize, timeout=100)
            except usb.core.USBError as e:
                if e.errno == 60:
                    # logging.debug("[Errno 60] Operation timed out. Continuing...")
                    continue
                raise e

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
