from unittest.mock import patch, MagicMock
from kvm_serial.backend.mouse import MouseListener
from tests._utilities import MockSerial, mock_serial


class TestMouse:
    @patch("serial.Serial", MockSerial)
    @patch("kvm_serial.backend.mouse.DataComm")
    def test_mouse_listener(self, mock_datacomm, mock_serial):
        """Test basic MouseListener initialization"""
        # Ensure DataComm mock is properly configured
        mock_datacomm.return_value = MagicMock()

        listener = MouseListener(mock_serial)

        # Verify DataComm was initialized with our mock serial
        mock_datacomm.assert_called_once_with(mock_serial)
