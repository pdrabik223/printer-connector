import serial.tools.list_ports
from device_connector.marlin_device import MarlinDevice

from time import sleep

if __name__ == "__main__":
    available_ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(available_ports):
        print(f"Scanning port: '{port}', desc: '{desc}', hwid: '{hwid}")

    printer = MarlinDevice.connect_on_port("COM7")

    list = ["M140 S30",
            "M105",
            "M190 S30",
            "M104 S30",
            "M105",
            "M109 S30",
            "M82",
            "G28",
            "G1 Z15.0 F6000",
            "G92 E0",
            "G1 F200 E3",
            "G92 E0",
            "G92 E0",
            "G92 E0",
            "G1 F1500 E-6.5",
            "M107",
            "G0 F3600 X97.803 Y72.384 Z0.3",
            "G0 X96.407 Y76.838"]

    for command in list:
        print(command)
        printer.send_and_await(command)
        sleep(5)
