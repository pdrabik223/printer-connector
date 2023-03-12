import math
import time
from abc import abstractmethod
from typing import Optional, Tuple

import serial.tools.list_ports


def static_vars(**kwargs) -> callable:
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


def list_available_serial_ports():
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))


class Point3D:
    def __init__(self, x=0, y=0, z=0):
        self.x: Optional[float] = x
        self.y: Optional[float] = y
        self.z: Optional[float] = z

    def is_none(self):
        return self.x is None or self.y is None or self.z is None

    def from_tuple(self, position: Tuple[float, float, float]):
        self.x = position[0]
        self.y = position[1]
        self.z = position[2]

    def as_tuple(self) -> Optional[Tuple[float, float, float]]:
        return self.x, self.y, self.z


class Device:
    """
    **Base class for various printer devices.**
    """

    def __init__(self):
        self.current_position: Point3D = Point3D()
        self.x_size: float = 220
        self.y_size: float = 220
        self.z_size: float = 200
        self.speed: float = 900
        self.printer_home_time: int = 20

    def predict_time_of_execution(self, command):
        constant_connection_time = 0.2

        if "G28" in command:
            return self.printer_home_time

        if "G1" in command:
            dest = self.parse_move_command_to_position(command)

            if self.current_position.is_none():
                return 10
            else:
                dist_2_dest = math.sqrt(
                    pow(self.current_position.x - dest[0], 2)
                    + pow(self.current_position.y - dest[1], 2)
                    + pow(self.current_position.z - dest[2], 2)
                )

                return (dist_2_dest / self.speed) * 60 + constant_connection_time

        return 0

    def get_current_position(self) -> Optional[Tuple[float, float, float]]:
        return self.current_position.as_tuple()

    def set_current_position(self, x: float, y: float, z: float):
        self.current_position.from_tuple((x, y, z))

    def set_current_position_from_string(self, position: str):
        x, y, z = Device.parse_move_command_to_position(position)
        self.current_position.from_tuple((x, y, z))

    @staticmethod
    def parse_move_command_to_position(
            command: str,
    ) -> Optional[Tuple[float, float, float]]:
        # Fuck me, get uot with this weak ass shit
        command = command.casefold() + " "

        if "x" in command:
            x_val_begin = command.find("x")
            if command[x_val_begin + 1] != " ":
                command = command[:x_val_begin] + " " + command[x_val_begin:]

            x_val_begin += 2

            x_val_end = command[x_val_begin:].find(" ")
            x = float(command[x_val_begin: x_val_end + x_val_begin])

        else:
            x = None

        if "y" in command:
            y_val_begin = command.find("y")

            if command[y_val_begin + 1] != " ":
                command = command[:y_val_begin] + " " + command[y_val_begin:]

            y_val_begin += 2
            y_val_end = command[y_val_begin:].find(" ")
            y = float(command[y_val_begin: y_val_end + y_val_begin])

        else:
            y = None

        if "z" in command:
            z_val_begin = command.find("z")
            if command[z_val_begin + 1] != " ":
                command = command[:z_val_begin] + " " + command[z_val_begin:]

            z_val_begin += 2
            z_val_end = command[z_val_begin:].find(" ")
            z = float(command[z_val_begin: z_val_end + z_val_begin])

        else:
            z = None

        return x, y, z
    @abstractmethod
    def send_and_await(self, command: str) -> str:
        """
        **Send command and await response.**
        Depending on used software, response might be returned as soon as command is acknowledged by the device,
        or after completion. Function will block thread and wait for response,
        after predefined tine function will return received message or 'no message received' error.

        Parameters
        ----------
        **command : str**
            Command send to device

        Returns
        -------
        **str**
            Response from device
        """
        pass

    @staticmethod
    @abstractmethod
    def connect_on_port(port: str, baudrate: int = 250000, timeout: int = 5) -> "Device":
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
        **Device**
           Correctly set up connector to printer device
        """
        pass

    @staticmethod
    @abstractmethod
    def connect() -> "Device":
        """
        **Search for port on which printed device is connected to pc.**
        If none is found, error is raised.

        Returns
        -------
        **Device**
            Correctly set up connector to printer device.
        """
        pass


if __name__ == "__main__":
    print(Device.parse_move_command_to_position("G1 X 32 Y 0.12 Z 12"))
