import sys
import glob
import serial
import termios
import logging

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

def list_serial_ports():
    """
    List serial port names on Windows, Mac, and Linux.
    """
    if sys.platform.startswith('win'):
        ports = [f'COM{i + 1}' for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        # On macOS, /dev/tty.* are "call-in" devices (used for incoming connections, e.g., modems waiting for a call),
        # and /dev/cu.* are "call-out" devices (used for outgoing connections, e.g., when your program initiates a connection).
        # /dev/cu.* is usually preferred for initiating connections from user programs.
        ports = glob.glob('/dev/cu.*')
        # Move cu.usbserial-xxxxxx ports to the end of the list
        usbserial_ports = [p for p in ports if 'cu.usbserial-' in p]
        other_ports = [p for p in ports if 'cu.usbserial-' not in p]
        ports = other_ports + usbserial_ports
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            # Only import if working
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, ImportError) as e:
            # Don't append ports we can't open
            logging.error(f"{port} could not be opened: {e}")
        except termios.error as e:
            logging.warning(f"{port} didn't open at 9600 baud, but a different rate may work!")
            result.append(port)
        except Exception as e:
            raise e
    return result
