import time
from typing import Union, Optional
from hameg3010.hameg3010device import Hameg3010Device
from hameg3010.hameg3010device_mock import Hameg3010DeviceMock
from src.assets.ci_colors import Colors
from src.hampd_config import HapmdConfig


def get_level(
    device: Union[Hameg3010Device, Hameg3010DeviceMock], frequency: int
) -> float:
    device.send_await_resp(f"rmode:frequency {frequency}")
    time.sleep(2)
    value: float = 1
    counter: int = 0
    while value > 0 or value < -100:
        level_raw: str = device.send_await_resp("rmode:level?")[1][2:-1]
        try:
            level = level_raw[level_raw.find(",") + 1 :]
            value = float(level)

        except Exception as ex:
            print(f"Encountered Error: {str(ex)}, retrying readout")

        counter += 1
        if counter == 10:
            return None

    return value


def set_up_hameg_device(
    hapmd_config: HapmdConfig,
) -> Optional[Union[Hameg3010Device, Hameg3010DeviceMock]]:
    try:
        hameg_device = Hameg3010Device.connect_using_vid_pid(
            hapmd_config.hameg_vid, hapmd_config.hameg_pid
        )

        print("Hameg device set up: " + Colors.OKGREEN + "OK" + Colors.ENDC)
        print(
            f"""
IDN              : {Colors.BOLD}{hameg_device.send_await_resp("*IDN?")[1][2:-1]}{Colors.ENDC}
Software Version : {Colors.BOLD}{hameg_device.send_await_resp("SYSTem:SOFTware?")[1][2:-1]}{Colors.ENDC}
Hardware Version : {Colors.BOLD}{hameg_device.send_await_resp("SYSTem:HARDware?")[1][2:-1]}{Colors.ENDC}
            """
        )
        # clean errors
        hameg_device.send_await_resp("SYSTem:ERRor:ALL?")

    except Exception as ex:
        print("Hameg device set up: " + Colors.FAIL + "FAIL" + Colors.ENDC)
        print(str(ex))
        hameg_device = None

    return hameg_device
