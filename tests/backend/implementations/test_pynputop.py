from unittest.mock import patch

from kvm_serial.backend.implementations.pynputop import PynputOp
from tests._utilities import MockSerial, mock_serial


class TestPynputOperation:
    @patch("serial.Serial", MockSerial)
    def test_name_property(self, mock_serial):
        """Test that the name property returns 'pynput'"""
        op = PynputOp(mock_serial)
        assert op.name == "pynput"
