from g_code_file_handler.g_code_file import GCodeFile
from configs.exceptions import EndofFile
from printer_connector.anycubic_s_device import AnycubicSDevice
import time
from serial import SerialException


def print_from_file(printer: AnycubicSDevice, file: GCodeFile) -> None:
    print("Commencing Printing.")
    while True:
        try:
            command = file.next_gcode_command()

            print(command)
            printer.send((command))

        except EndofFile as ex:
            print("Printing completed.")
            return None


import serial


if __name__ == "__main__":
    ser = serial.Serial("COM3", 115200)
    print("await")
    time.sleep(20)
    print("zero axis")
    ser.write(str.encode("G28 W\r\n"))
    print("written")
    time.sleep(20)

    ser.close()

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
