import time
from serial import Serial


class AnycubicSDevice:
    _device: Serial = None  # pyserial connector device

    def __init__(self, device) -> None:
        self._device = device

    def __del__(self):
        self._device.close()

    @staticmethod
    def connect_on_port(
        port: str, baudrate: int = 115200, timeout=5
    ) -> "AnycubicSDevice":
        dev = AnycubicSDevice(
            device=Serial(port=port, baudrate=baudrate, timeout=timeout)
        )
        time.sleep(2)

        resp = dev._device.readline()

        while str(resp) != "b''":
            print(resp)
            resp = dev._device.readline()

        return dev

    def send_and_await(self, command: str) -> str:
        """
        send command to Anycubic S device, than await response

        Args:
            command (str): g-code command

        Returns:
            str: response from device
        """

        if command[-1] != "\n":
            command += "\n"

        print(bytearray(command, "ascii"))
        self._device.write(bytearray(command, "ascii"))

        resp = ""

        for _ in range(10):
            resp = str(self._device.readline())
            if resp != "":
                break
        return resp

    @staticmethod
    def checksum(line):
        cs = 0
        for i in range(0, len(line)):
            cs ^= ord(line[i]) & 0xFF
        cs &= 0xFF
        return str(cs)

    @staticmethod
    def csline(line):
        return line + "*" + AnycubicSDevice.checksum(line)
