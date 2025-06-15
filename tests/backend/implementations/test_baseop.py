from unittest.mock import patch, MagicMock
from kvm_serial.backend.implementations.baseop import KeyboardOp


class ConcreteKeyboardOp(KeyboardOp):
    """Concrete implementation of KeyboardOp for testing"""

    def run(self):
        return True

    def cleanup(self):
        pass

    @property
    def name(self):
        return "test_keyboard"


class TestKeyboardOpImplementation:
    """Test suite for KeyboardOp base class implementation"""

    @patch("serial.Serial")
    @patch("kvm_serial.backend.implementations.baseop.DataComm")
    def test_init(self, mock_datacomm, mock_serial):
        """Test initialization of KeyboardOp"""
        mock_serial.port = "/dev/ttyUSB0"
        mock_serial.is_open = True
        mock_serial.baudrate = 9600

        # Create instance
        op = ConcreteKeyboardOp(mock_serial)

        # Verify initialization
        assert op.serial_port == mock_serial
        assert op.name == "test_keyboard"

        # Verify DataComm was initialized with correct serial port
        assert isinstance(op.hid_serial_out, MagicMock)
        mock_datacomm.assert_called_once_with(mock_serial)
