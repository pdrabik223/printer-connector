from g_code_file_handler.g_code_file import GCodeFile
from configs.exceptions import EndofFile
from printer_connector.anycubic_s_device import AnycubicSDevice
import time
from serial import SerialException

from printer_connector.device import Device
from printer_connector.prusa_device import PrusaDevice


def print_from_file(printer: Device, file: GCodeFile) -> None:
    print("Commencing Printing.")
    while True:
        try:
            command = file.next_gcode_command()
            print(command)
            printer.send((command))

        except EndofFile as ex:
            print("Printing completed.")
            return None


if __name__ == "__main__":


    printer = PrusaDevice.connect()

    # for i in range(1, 14):
    #     print(f"COM{i}")

    #     try:
    #         printer = AnycubicSDevice.connect_on_port(f"COM{i}", 115200)
    #         break

    #     except SerialException:
    #         continue
    # print("great, back to conncetor")
    # time.sleep(2)
    # print("temp1")
    # print(printer.send_and_await("G28 W"))

    # time.sleep(2)
    # print("temp2")
    # print(printer.send_and_await("M104 S30"))

    # time.sleep(2)
    # print("temp3")
    # print(printer.send_and_await("M104 S185"))
