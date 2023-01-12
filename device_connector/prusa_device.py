import enum
import time
from serial import Serial
from serial import SerialException
from typing import Optional
from device_connector.device import Device
import serial.tools.list_ports


class PrusaDevice(Device):
    _device: Serial = None  # pyserial connector device

    def __init__(self, device) -> None:
        self._device = device

    # TODO READ on self
    def __del__(self) -> None:
        if self._device is None:
            return
        commands = [
            # "G1 Z4 F720",  # Move print head up
            "G1 X0 Y200 F3600",  # park
            # "G1 Z52 F720",  # Move print head further up
            "G4",  # wait
            "M221 S100",  # reset flow
            "M900 K0",  # reset LA
            "M907 E538",  # reset extruder motor current
            "M104 S0",  # turn off temperature
            "M140 S0",  # turn off heated
            "M107 M84",  # turn off fan  # disable motors
        ]
        for command in commands:
            self.send_and_await(command=command)

        self._device.close()

    @staticmethod
    def connect_on_port(port: str, baudrate: int = 115200, timeout=2) -> "PrusaDevice":
        """
        Connect to Prusa device
        Args:
            port (str): COM port on windows system, usually 9.
            baudrate (int, optional): baudrate. Defaults to 115200.
            timeout (int, optional): timeout. Defaults to 5.

        Returns:
            PrusaDevice: _description_
        """
        device = Serial(port=port, baudrate=baudrate, timeout=timeout)
        time.sleep(2)

        resp = device.readline().decode("utf-8")

        while resp != "":
            print(resp.strip())
            resp = device.readline().decode("utf-8")

        return PrusaDevice(device)

    @staticmethod
    def connect() -> "PrusaDevice":
        baudrate: int = 250000
        timeout: int = 1
        device: Optional[Serial] = None
        available_ports = serial.tools.list_ports.comports()

        for port, desc, hwid in sorted(available_ports):
            print(f"Scanning port: '{port}', desc: '{desc}', hwid: '{hwid}")
            try:
                device: Serial = Serial(
                    port=str(port), baudrate=baudrate, timeout=timeout
                )
                print(f"Serial port is Open'")

                resp: bytes = device.read_all().decode("utf-8")
                print(f"Answer: '{resp}'")

                # if resp != "start\n":
                #     raise SerialException()

                print(f"Connected on port: '{port}', desc: '{desc}', hwid: '{hwid}")

                break

            except SerialException:
                device = None
                continue
        if not device:
            raise SerialException("Device not found")

        while resp != "":
            print(resp.strip())
            resp = device.readline().decode("utf-8")

        return PrusaDevice(device=device)

    class PrusaPrinterStatus(enum.Enum):
        PROCESSING = 'processing'
        READY = 'ready'

    def send_and_await(self, command: str) -> str:

        """
        send command to Prusa device, then await response

        Args:
            command (str): g-code command

        Returns:
            str: response from device
        """
        if command[-1] != "\n":
            command += "\n"

        self._device.write(bytearray(command, "utf-8"))
        if "G1" in command:
            time.sleep(5)

        elif "G28" in command:
            time.sleep(30)

        resp = ""
        retries = 5
        r = 0
        # after every successfully completed command, prusa returns 'ok' message
        while "ok" not in resp:
            resp = str(self._device.readline().decode("utf-8"))
            print(resp.strip())
            if 'busy' in resp:
                print("awaiting 2s")
                time.sleep(2)
            else:
                r += 1
                if r > retries:
                    return "none message"

    def startup_procedure(self) -> None:
        """
        send default parameters (motor speed, acceleration, model check, etc...)
        and zero all the axies
        """
        commands = [
            "M201 X1000 Y1000 Z200 E5000",
            "M203 X200 Y200 Z12 E120",
            "M204 P1250 R1250 T1250",
            "M205 X8.00 Y8.00 Z0.40 E4.50",
            "M205 S0 T0",
            "M107",
            'M862.3 P "MK3S"',
            "G90",
            "G28 W",
        ]
        for command in commands:
            self.send_and_await(command=command)
