from g_code_file_handler.g_code_file import GCodeFile
from configs.exceptions import EndofFile
from printer_connector.anycubic_s_device import AnycubicSDevice
from printer_connector.anycubic_kobra_device import AnycubicKobraDevice

import time
from serial import SerialException


if __name__ == "__main__":
    printer = AnycubicKobraDevice.connect()

    print("great, back to connector")
    time.sleep(2)
    print("req:  M110")
    print("resp: " + str(printer.send_and_await("M110")))

    time.sleep(2)
    print("req:  G28")
    print("resp: " + str(printer.send_and_await("G28")))

    print("req:  G1 X100 Y100 Z10")
    print("resp: " + str(printer.send_and_await("G1 X100 Y100 Z10")))

    print("req:  G28")
    print("resp: " + str(printer.send_and_await("G28")))

    print("req:  G1 X100 Y100 Z10")
    print("resp: " + str(printer.send_and_await("G1 X100 Y100 Z10")))
