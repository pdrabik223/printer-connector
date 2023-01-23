import pytest

from printer_device_connector.device import Device
from printer_device_connector.prusa_device import PrusaDevice


class TestPrinterDevice:
    def test_parse_move_command_to_position(self):
        command = "G1 X 32 Y 0.12 Z 12"
        assert Device.parse_move_command_to_position(command) == (32, 0.12, 12)
