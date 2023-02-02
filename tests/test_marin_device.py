import pytest
from printer_device_connector.marlin_device import MarlinDevice


class TestMarlinDevice:
    def test_no_line(self):
        lines = ("0", "1", "2", "G1")
        numbered_lines = ("N00N0", "N11N1", "N22N2", "N3G1N3")
        for l, n in zip(lines, numbered_lines):
            n == MarlinDevice.no_line(l)

    @pytest.mark.parametrize(
        "example", (("0", 48), ("1", 49), ("2", 50), ("G1", 118), ("N1G1N1", 118))
    )
    def test_check_sum(self, example):
        test, expected_value = example
        assert expected_value == MarlinDevice.checksum(test)

    @pytest.mark.parametrize(
        "example",
        (
            ("0", "0*48"),
            ("1", "1*49"),
            ("2", "2*50"),
            ("G1", "G1*118"),
            ("N1G1N1", "N1G1N1*118"),
        ),
    )
    def test_cs_line(self, example):
        test, expected_value = example
        assert expected_value == MarlinDevice.cs_line(test)
