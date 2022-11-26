import pytest
from printer_connector.exceptions import (
    InvalidGCodeFileExtension,
    UnsupportedSlicerVendor,
)
from printer_connector.g_code_file import GCodeFile
from printer_connector.configs import SlicerVendor


class TestGCodeFile:
    def test_incorrect_gcode_file_path(self):
        with pytest.raises(FileNotFoundError) as ex:
            GCodeFile("not_a_valid_path.gcode")

    def test_incorrect_gcode_file_extension(self):
        with pytest.raises(InvalidGCodeFileExtension) as ex:
            GCodeFile("not_a_valid_path.txt")
            assert "Expected '.gcode', got 'th.txt'" in str(ex)

    def test_correct_read_slicer_vendor_prusa(self):
        file = GCodeFile("assets/testing_block_0.1mm_PLA_MK3S_9m.gcode")
        assert file.read_slicer_vendor() == SlicerVendor.PrusaSlicer

    def test_correct_read_slicer_vendor_cura(self):
        file = GCodeFile("assets/anycubic_cobra_testing_block.gcode")
        assert file.read_slicer_vendor() == SlicerVendor.Cura

    def test_un_supported_vendor(self):
        with pytest.raises(UnsupportedSlicerVendor) as ex:
            GCodeFile("assets/default_gcode_vendor.gcode").read_slicer_vendor()

    @pytest.mark.parametrize(
        "line", (";it is comment", "    ;comment", " \t;comment", ";comment\n")
    )
    def test_correct_is_comment(self, line):
        assert GCodeFile.is_comment(line)

    @pytest.mark.parametrize(
        "line", ("not a comment", "G1 X69", " \tcomment", "G1 X69 ;comment\n")
    )
    def test_incorrect_is_comment(self, line):
        assert not GCodeFile.is_comment(line)

    @pytest.mark.parametrize("line", (" ", "    ", " \t", " \t\n"))
    def test_correct_is_empty(self, line):
        assert GCodeFile.is_empty(line)

    @pytest.mark.parametrize(
        "line",
        (
            "not a comment",
            "G1 X69",
            " \tcomment",
            "G1 X69 ;comment\n",
            ";it is comment",
            "    ;comment",
            " \t;comment",
            ";comment\n",
        ),
    )
    def test_incorrect_is_not_empty(self, line):
        assert not GCodeFile.is_empty(line)

    def test_next_gcode_command_success_prusa_slicer(self):
        file = GCodeFile("assets/testing_block_0.1mm_PLA_MK3S_9m.gcode")
        assert file.next_gcode_command() == "M73 P0 R9"

    def test_next_gcode_command_success_cura(self):
        file = GCodeFile("assets/anycubic_cobra_testing_block.gcode")
        assert file.next_gcode_command() == "M140 S60"
