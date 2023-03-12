import time
from typing import Tuple
from typing import Optional
from serial import Serial
from serial import SerialException
from printer_device_connector.device import Device, static_vars
from printer_device_connector.exceptions import Err, ResultWithErr

import serial.tools.list_ports
import logging


class MarlinDevice(Device):
    """
    **Marlin Device Connector**
    Specification of Connector class for printers running marlin os.

    (**Marlin Firmware on github:**)[https://github.com/MarlinFirmware/Marlin]
    https://github.com/MarlinFirmware/Marlin

    """

    _SUCCESSFUL_CONNECTION_MESSAGE = bytes("start\n", "utf-8")

    _device: Serial  # pyserial connector device

    def __init__(self, device: Serial) -> None:
        super().__init__()
        self._device = device

    def __del__(self) -> None:
        self._device.close()

    @staticmethod
    def connect_on_port(port: str, baudrate: int = 250000, timeout=5) -> "MarlinDevice":
        """
        **Connects to device on specified port.**

        Parameters
        ----------
        **port : str**
            Port on witch Printer device is connected

        **baudrate : int, optional**
            Information transfer speed (in bits per second), **by default 250000**

        **timeout : int, optional**
            Await for response time in seconds, **by default 5**

        Returns
        -------
        **MarlinDevice**
           Correctly set up connector to printer device
        """
        device = Serial(port=port, baudrate=baudrate, timeout=timeout)
        print("connected")
        resp: bytes = device.readline()
        print(resp.strip())

        while resp != bytes():
            if resp is not None:
                resp = device.readline()
                print(resp.strip())

        return MarlinDevice(device=device)

    @staticmethod
    def connect() -> "MarlinDevice":
        """
        **Search for port on which printed device is connected to pc.**
        If none is found, error is raised.

        Marlin device runs on: **baudrate set to 250000**

        Raises
        ------

        Returns
        -------
        **MarlinDevice**
            Correctly set up connector to printer device.
        """
        baudrate: int = 250000
        timeout: int = 1
        device: Optional[Serial] = None
        available_ports = serial.tools.list_ports.comports()

        print("List all available ports:")
        for port, desc, hwid in sorted(available_ports):
            print(f"\t port: '{port}', desc: '{desc}', hwid: '{hwid}")

        for port, desc, hwid in sorted(available_ports):
            print(
                f"Connected connecting to:\n\t port: '{port}', desc: '{desc}', hwid: '{hwid}"
            )
            try:
                device: Serial = Serial(
                    port=str(port), baudrate=baudrate, timeout=timeout
                )
                print(f"Serial port is Open'")
                resp: bytes = device.readline()
                print(f"Answer: '{resp}'")

                if resp != MarlinDevice._SUCCESSFUL_CONNECTION_MESSAGE:
                    raise SerialException()

                print(f"Connected on port: '{port}', desc: '{desc}', hwid: '{hwid}")
                logging.info(
                    f"Connected on port: '{port}', desc: '{desc}', hwid: '{hwid}"
                )
                break

            except SerialException:
                device = None
                continue

        if device is None:
            raise SerialException("Device not found")

        while resp != "":
            if resp is not None:
                resp = device.readline().decode("utf-8")
                print(resp.strip())

        return MarlinDevice(device=device)

    def send_and_await(self, command: str) -> Tuple[str, str]:
        """
        send command to Anycubic S device, then await response

        Args:
            command (str): g-code command

        Returns:
            str: response from device
        """

        if "F" not in command:
            command += f" F {self.speed}"

        command = MarlinDevice.no_line(command)
        command = MarlinDevice.cs_line(command)

        if command[-1] != "\n":
            command += "\n"

        print(f"req:  {command}")
        print(f"predicted_time_of_execution: {self.predict_time_of_execution(command)}")

        self._device.write(bytearray(command, "ascii"))
        time.sleep(self.predict_time_of_execution(command))

        resp = str(self._device.readline())
        print(f"resp: {resp}")

        if "G1" in command:
            self.set_current_position_from_string(command)

        elif "G28" in command:
            self.current_position.from_tuple((0, 0, 0))

        return (resp, resp[2:-3])

    @staticmethod
    def checksum(line: str) -> int:
        cs = 0
        for i in range(0, len(line)):
            cs ^= ord(line[i]) & 0xFF
        cs &= 0xFF
        return cs

    @staticmethod
    def cs_line(line: str) -> str:
        return line + "*" + str(MarlinDevice.checksum(line))

    @staticmethod
    @static_vars(line_counter=1)
    def no_line(line: str) -> str:
        line = (
            f"N{MarlinDevice.no_line.line_counter} "
            + line
            + f" N{MarlinDevice.no_line.line_counter}"
        )
        MarlinDevice.no_line.line_counter += 1

        return line

    def startup_procedure(self):
        self.send_and_await("G28")
