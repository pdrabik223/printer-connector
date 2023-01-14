import math
import random
from typing import Any
import logging


class DeviceMock:
    current_frequency = 1_000_000
    receiver_mode = "RMODE"
    freq_value_mapping = {}

    def __init__(self) -> None:
        pass

    @staticmethod
    def connect_using_vid_pid(idVendor, idProduct):
        logging.debug(
            f"Connected to mock device with pid: {idProduct}, vid: {idVendor}"
        )
        return DeviceMock()

    def func(self):
        if self.current_frequency not in self.freq_value_mapping.keys():
            self.freq_value_mapping[self.current_frequency] = random.random() * math.pi

        new_value = math.sin(self.freq_value_mapping[self.current_frequency]) * 35 - 40
        self.freq_value_mapping[self.current_frequency] += 0.025

        # if new_value < -80:
        #     new_value = new_value + (0.1*new_value)
        # elif new_value > -10:
        #     new_value = new_value - (0.1*new_value)
        # elif random.random() < 0.5:
        #     new_value = new_value + (0.1*new_value)
        # else:
        #     new_value = new_value - (0.1*new_value)

        return new_value

    def send_await_resp(self, cmd: str) -> Any:
        cmd = cmd.casefold()
        if cmd == "*idn?":
            return (
                "1'HAMEG IDN 123324.1231",
                "1'HAmeg 12.11 I need some C2H6O stat \n",
            )
        elif cmd == "system:software?":
            return ("1'idk like 12", "1'idk like 12 i'm not good with numbers\n")
        elif cmd == "system:hardware?":
            return ("1'idk like 12", "1'idk like 11 this thinking is killing me\n")
        elif cmd == "system:mode?":
            return (f"1'{self.receiver_mode}", f"1'{self.receiver_mode}\n")
        elif cmd == "rmode:frequency?":
            return (f"1'{self.current_frequency}", f"1'{self.current_frequency}\n")
        elif cmd == "rmode:level?":
            return (
                f"1'{self.current_frequency},{self.func()}",
                f"1'{self.current_frequency},{self.func()}\n",
            )
        elif "rmode:frequency" in cmd:
            self.current_frequency = float(cmd[15:])
        elif "system:mode" in cmd:
            self.receiver_mode = cmd[11:]
        return ("1'", "")
