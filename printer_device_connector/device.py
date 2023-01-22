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


class Position:
    def __init__(self):
        self.x: Optional[float] = None
        self.y: Optional[float] = None
        self.z: Optional[float] = None

    def is_none(self):
        return self.x is None or self.y is None or self.z is None

    def from_tuple(self, position: Tuple[float, float, float]):
        self.x = position[0]
        self.y = position[1]
        self.z = position[2]

    def to_tuple(self) -> Optional[Tuple[float, float, float]]:
        if self is None:
            return None
        return tuple(self.x, self.y, self.z)


class Device:
    """
    **Base class for various printer devices.**
    """

    def __init__(self):
        self.current_position: Position = Position()

    def get_current_position(self) -> Optional[Tuple[float, float, float]]:
        return self.current_position.to_tuple()

    def set_current_position(self, x: float, y: float, z: float):
        self.current_position.from_tuple((x, y, z))

    def set_current_position_from_string(self, position: Tuple[float, float, float]):
        self.current_position.from_tuple(position)

    @staticmethod
    def parse_move_command_to_position(command: str) -> Optional[Tuple[float, float, float]]:
        x_pos = command.find("X")
        y_pos = command.find("Y")
        z_pos = command.find("Z")

        split_by_space = command.split(" ")

        if x_pos != -1:
            pass

        if y_pos != -1:
            pass

        if z_pos != -1:
            pass

    def send_and_await(self, command: str) -> str:
        """
        **Send command and await response.**
        Depending on used software, response might be returned as soon as command is acknowledged by the device, or after completion.
        Function will block thread and wait for response, after predefined tine function will return received message or 'no message received' error.

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

    def connect_on_port(
            port: str, baudrate: int = 250000, timeout: int = 5
    ) -> "Device":
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
