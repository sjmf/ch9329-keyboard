class DataComm:
    """
    DataComm class based on beijixiaohu/ch9329Comm module; simplified and commented
    Original: https://github.com/beijixiaohu/CH9329_COMM/ / https://pypi.org/project/ch9329Comm/
    """

    def __init__(self, port):
        self.port = port

    def send(self, data: bytes, head = b'\x57\xAB', addr = b'\x00', cmd=b'\x02'):
        """
        Convert input to data packet and send command over serial.

        Args:
            data: data packet to encapsulate and send
            head: Packet header
            addr: Address
            cmd: Data command (0x02 = Keyboard; 0x04 = Absolute mouse; 0x05 = Relative mouse)
        Returns:
            True if successful, otherwise throws an exception
        """
        length = len(data).to_bytes(1, 'little')

        # Calculate checksum
        checksum = (
            sum(head) +
            int.from_bytes(addr, 'big') +
            int.from_bytes(cmd, 'big') +
            int.from_bytes(length, 'big') +
            sum(data)
        ) % 256

        # Build data packet
        packet = head + addr + cmd + length + data + bytes([checksum])

        # Write command to serial port
        self.port.write(packet)  
        
        return True

    def send_scancode(self, scancode: bytes):
        if len(scancode) < 8:
            return False

        self.send(scancode)

    def release(self):
        """
        Release the button.

        Return:
            None
        """
        self.send(b'\x00' * 8)
