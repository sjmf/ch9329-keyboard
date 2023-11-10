class DataComm:
    """
    DataComm class from pypi ch9329Comm module translated from Chinese and simplified to work
    using keyboard scancodes https://pypi.org/project/ch9329Comm/
    """

    def __init__(self, port):
        self.port = port

    def send_scancode(self, scancode: bytes):
        if len(scancode) < 8:
            return False

        self.send(scancode)

    def send(self, DATA):
        # Convert characters to packets
        HEAD = b'\x57\xAB'  # Frame header
        ADDR = b'\x00'  # address
        CMD = b'\x02'  # command
        LEN = b'\x08'  # data length

        # Simple checksums:
        # Separate the values in HEAD and calculate the sum
        HEAD_add_hex_list = sum([byte for byte in HEAD])
        # Separate the values in DATA and calculate the sum
        DATA_add_hex_list = sum([byte for byte in DATA])

        # Calculate checksum
        try:
            SUM = (
                sum(
                    [
                        HEAD_add_hex_list,
                        int.from_bytes(ADDR, byteorder='big'),
                        int.from_bytes(CMD, byteorder='big'),
                        int.from_bytes(LEN, byteorder='big'),
                        DATA_add_hex_list,
                    ]
                )
                % 256
            )  # Checksum
        except OverflowError:
            print("int too big to convert")
            return False

        packet = HEAD + ADDR + CMD + LEN + DATA + bytes([SUM])  # Data packet
        self.port.write(packet)  # Write command code to serial port
        return True  # Returns True if successful, otherwise throws an exception

    def release(self):
        """
        Release the button.

        Return:
            None
        """
        self.send(b'\x00' * 8)
