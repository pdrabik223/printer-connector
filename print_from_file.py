from g_code_file_handler.g_code_file import GCodeFile
from configs.exceptions import EndofFile
from device_connector.marlin_device import MarlinDevice
import time
from serial import SerialException

from device_connector.device import Device
from device_connector.prusa_device import PrusaDevice


def print_from_file(printer: Device, file: GCodeFile) -> None:
    print("Commencing Printing.")
    while True:
        try:
            command = file.next_gcode_command()
            print(command)
            # printer.send_and_await(command)

        except EndofFile as ex:
            print("Printing completed.")
            return None


if __name__ == "__main__":
    printer = MarlinDevice.connect_on_port("COM8")
    file = GCodeFile(file_name="C:\D\desk-spacer v6_0.15mm_PLA_MK3S_16m.gcode")
    print_from_file(printer=printer, file=file)
