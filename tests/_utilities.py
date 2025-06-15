from pytest import fixture
from unittest.mock import MagicMock
from typing import Optional
from io import StringIO


class MockSerial:
    """Mock class for Serial object"""

    def __init__(self, port=None) -> None:
        self.output = StringIO()
        self.fd = self.output

        self.is_open: bool = False
        self.portstr: Optional[str] = None
        self.name: Optional[str] = None

        self.write = MagicMock(return_value=1)  # Mock the write method
        self.close = MagicMock(return_value=1)  # ...      close method


@fixture
def mock_serial():
    return MockSerial()
