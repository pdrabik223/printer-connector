import time
from serial import Serial
from serial import SerialException

from device_connector.device import Device


class PrusaDevice(Device):
    _device: Serial = None  # pyserial connector device

    def __init__(self, device) -> None:
        self._device = device

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
            "M140 S0",  # turn off heatbed
            "M107" "M84",  # turn off fan  # disable motors
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
        dev = PrusaDevice(device=Serial(port=port, baudrate=baudrate, timeout=timeout))
        time.sleep(2)

        resp = dev._device.read_all().decode("utf-8")

        while resp != "":
            print(resp.strip())
            resp = dev._device.read_all().decode("utf-8")

        return dev

    @staticmethod
    def connect() -> "PrusaDevice":
        baudrate: int = 115200
        timeout = 2

        for i in range(1, 14):
            try:
                port: str = f"COM{i}"
                device = Serial(port=port, baudrate=baudrate, timeout=timeout)

                resp = device.read_all().decode("utf-8")
                if resp != "start\n":
                    raise SerialException()

                print(f"connected on port '{port}'")
                break

            except SerialException:
                continue

        while resp != "":
            print(resp.strip())
            resp = device.read_all().decode("utf-8")

        return PrusaDevice(device=device)

    def send_and_await(self, command: str) -> str:
        """
        send command to Prusa device, than await response

        Args:
            command (str): g-code command

        Returns:
            str: response from device
        """
        if command[-1] != "\n":
            command += "\n"

        self._device.write(bytearray(command, "utf-8"))

        resp = ""
        retries = 3
        r = 0
        # after every successfully completed command, prusa returns 'ok' message
        while "ok" not in resp:

            resp = str(self._device.read_all().decode("utf-8"))
            print(resp.strip())
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
            self._device.send_and_await(command=command)
