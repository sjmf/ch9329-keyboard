from unittest.mock import patch, MagicMock

from kvm_serial.backend.implementations.pynputop import PynputOp
from tests._utilities import MockSerial, mock_serial


# Mock the entire pynput.keyboard module
@patch("kvm_serial.backend.implementations.pynputop.Key")
@patch("kvm_serial.backend.implementations.pynputop.KeyCode")
@patch("kvm_serial.backend.implementations.pynputop.Listener")
@patch("serial.Serial", MockSerial)
class TestPynputOperation:
    def test_name_property(self, mock_serial, mock_listener, mock_keycode):
        """Test that the name property returns 'pynput'"""
        op = PynputOp(mock_serial)
        assert op.name == "pynput"
