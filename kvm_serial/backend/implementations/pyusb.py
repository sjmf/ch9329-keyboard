# PyUSB implementation
import logging
import usb.core
from usb.core import Device, Interface
from kvm_serial.utils.utils import scancode_to_ascii
from .baseop import KeyboardOp

logger = logging.getLogger(__name__)


class PyUSBOp(KeyboardOp):
    """
    PyUSB operation mode: supports all modifier keys, requires superuser.
    """

    @property
    def name(self):
        return "usb"

    def __init__(self, serial_port):
        super().__init__(serial_port)
        self.usb_endpoints = get_usb_endpoints()

    def run(self):
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
            endpoint, dev, interface_number = [*self.usb_endpoints.values()][0]
            self.debounce = None

            # Detach kernel driver to perform raw IO with device (requires elevated sudo privileges)
            # Otherwise you will receive "[Errno 13] Access denied (insufficient permissions)"
            if dev.is_kernel_driver_active(interface_number):
                dev.detach_kernel_driver(interface_number)

            logging.info("Press Ctrl+ESC to exit")
            while self._parse_key(endpoint):
                pass

        except usb.core.USBError as e:
            logging.error(e)

        finally:
            usb.util.dispose_resources(dev)
            if dev is not None:
                dev.attach_kernel_driver(interface_number)

    def _parse_key(self, endpoint):
        # Read keyboard scancodes
        try:
            data_in = endpoint.read(endpoint.wMaxPacketSize, timeout=100)
        except usb.core.USBError as e:
            if e.errno == 60:
                # logging.debug("[Errno 60] Operation timed out. Continuing...")
                return True
            raise e

        # Debug print scancodes:
        logging.debug(
            f"{data_in}, \t"
            f"({', '.join([hex(i) for i in data_in])})\t"
            f"{scancode_to_ascii(data_in)}"
        )

        # Check for escape sequence (and helpful prompt)
        if data_in[0] == 0x1 and data_in[2] == 0x6 and self.debounce != "c":  # Ctrl+C:
            logging.warning("\nCtrl+C passed through. Use Ctrl+ESC to exit!")

        if data_in[0] == 0x1 and data_in[2] == 0x29:  # Ctrl+ESC:
            logging.warning("\nCtrl+ESC escape sequence detected! Exiting...")
            return False

        key = scancode_to_ascii(data_in)

        if key != self.debounce and key:
            print(key, end="", flush=True)
            self.debounce = key
        elif not key:
            self.debounce = None

        return self.hid_serial_out.send_scancode(data_in)


def get_usb_endpoints():
    endpoints = {}

    # Find all USB devices
    try:
        devices = usb.core.find(find_all=True)
    except usb.core.NoBackendError as e:
        logging.error(
            "The PyUSB library cannot find a suitable USB backend (such as libusb)"
            " on your system. Install one using your system's package manager, e.g.:\n"
            "\t$ sudo apt-get install libusb-1.0-0-dev (Debian/Ubuntu)\n"
            "\t$ sudo dnf install libusb1-devel (RHEL/Fedora)\n"
            "\t$ brew install libusb (MacOSX)\n"
        )
        raise e

    if devices is None:
        logging.warning("No USB devices found.")
        return endpoints

    # Iterate through connected USB devices
    for device in devices:
        # Ensure we only process Device objects (not Configuration)
        if not isinstance(device, Device):
            continue

        # Check if the device is a keyboard
        if getattr(device, "bDeviceClass") == 0 and getattr(device, "bDeviceSubClass") == 0:
            cfg = device.get_active_configuration()
            interface_number = list(cfg)[0].bInterfaceNumber
            intf = usb.util.find_descriptor(
                cfg,
                bInterfaceNumber=interface_number,
            )

            endpoint = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: (
                    usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
                    and usb.util.endpoint_type(e.bmAttributes) == usb.util.ENDPOINT_TYPE_INTR,
                ),
            )

            if not isinstance(intf, Interface) or not endpoint:
                continue

            # A keyboard will have the following: (https://wuffs.org/blog/mouse-adventures-part-5)
            # bInterfaceClass == 0x3
            # bInterfaceSubClass == 0x1
            # bInterfaceProtocol == 0x1 (mouse is protocol 0x2)
            if not (
                getattr(intf, "bInterfaceClass") == 0x03
                and getattr(intf, "bInterfaceSubClass") == 0x01
                and getattr(intf, "bInterfaceProtocol") == 0x01
            ):
                continue

            vendorID = getattr(device, "idVendor")
            productID = getattr(device, "idProduct")
            logger.info(
                f"Keyboard: vID: 0x{vendorID:04x}; "
                f"pID: 0x{productID:04x}; "
                f"if: {interface_number}"
            )
            logger.debug(intf)

            endpoints[f"{vendorID:04x}:{productID:04x}"] = (
                endpoint,
                device,
                interface_number,
            )

    return endpoints


def main_usb(serial_port):
    return PyUSBOp(serial_port).run()
