import time
from typing import Tuple
from serial import Serial
from serial import SerialException
from device_connector.device import Device


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


class AnycubicKobraDevice(Device):
    _device: Serial = None  # pyserial connector device

    def __init__(self, device) -> None:
        self._device = device

    def __del__(self):
        self._device.close()

    @staticmethod
    def connect_on_port(
        port: str, baudrate: int = 250000, timeout=5
    ) -> "AnycubicKobraDevice":

        dev = AnycubicKobraDevice(
            device=Serial(port=port, baudrate=baudrate, timeout=timeout)
        )
        time.sleep(2)

        resp = dev._device.readline()

        while str(resp) != "b''":
            print(resp)
            resp = dev._device.readline()

        return dev

    @staticmethod
    def connect() -> "AnycubicKobraDevice":
        baudrate: int = 250000
        timeout = 5

        for i in range(1, 14):
            try:
                port: str = f"COM{i}"
                device = Serial(port=port, baudrate=baudrate, timeout=timeout)

                resp = device.readline()
                if resp != "b'start\n'":
                    raise SerialException()

                print(f"connected on port '{port}'")
                break

            except SerialException:
                if i == 13:
                    raise SerialException("Device not found")
                continue

        while str(resp) != "b''":
            print(resp)
            resp = device.readline()

        return AnycubicKobraDevice(device=device)

    def send_and_await(self, command: str) -> Tuple[str, str]:
        """
        send command to Anycubic S device, than await response

        Args:
            command (str): g-code command

        Returns:
            str: response from device
        """
        command = AnycubicKobraDevice.no_line(command)
        command = AnycubicKobraDevice.cs_line(command)

        if command[-1] != "\n":
            command += "\n"

        self._device.write(bytearray(command, "ascii"))

        resp = str(self._device.readline())
        return (resp, resp[2:-3])

    @staticmethod
    def checksum(line: str):
        cs = 0
        for i in range(0, len(line)):
            cs ^= ord(line[i]) & 0xFF
        cs &= 0xFF
        return str(cs)

    @staticmethod
    def cs_line(line: str):
        return line + "*" + AnycubicKobraDevice.checksum(line)

    @staticmethod
    def no_line(line: str):

        try:
            AnycubicKobraDevice.no_line.line_counter += 1
        except Exception:
            AnycubicKobraDevice.no_line.line_counter = 0

        line = (
            f"N{AnycubicKobraDevice.no_line.line_counter} "
            + line
            + f" N{AnycubicKobraDevice.no_line.line_counter}"
        )

        return line
