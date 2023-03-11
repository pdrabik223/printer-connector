import time
from typing import Union
from hapmd.src.hameg3010.hameg3010device import Hameg3010Device
from hapmd.src.hameg3010.hameg3010device_mock import Hameg3010DeviceMock
import usb.core
import usb.util


def get_level(
    device: Union[Hameg3010Device, Hameg3010DeviceMock],
    frequency: int,
    measurement_time: int = 1,
) -> float:
    device.send_await_resp(f"rmode:mtime {measurement_time}")
    device.send_await_resp(f"rmode:frequency {frequency}")

    if isinstance(device, Hameg3010DeviceMock):
        time.sleep(1)
    else:
        time.sleep(measurement_time)

    level_raw: str = device.send_await_resp("rmode:level?")[1][2:-1]
    print(f"level_raw: {level_raw}")
    level = level_raw[level_raw.find(",") + 1:]

    value = float(level)

    return value


def hameg_console_loop(hameg_handle: Union[Hameg3010Device, Hameg3010DeviceMock]):
    while True:
        try:
            command = input("hameg> ")
            # command = command.casefold()
            command = command.replace(" ", "")
            if "read" in command.casefold():
                command = command[4:]
                if "ghz" in command.casefold():
                    val = float(command[:-3])
                    val *= 10**9
                else:
                    val = int(command)

                print(get_level(hameg_handle, val))

            if command in ("quit", "q"):
                return
            else:
                resp = hameg_handle.send_await_resp(command)
                print(f"response: {resp[1]}")
                print(
                    f"errors:   {hameg_handle.send_await_resp('SYSTem:ERRor:ALL?')[1][2:-1]}"
                )
        except Exception as ex:
            print(f"Command: {command} is not recognized")


def set_up_hamed_device(debug: bool = False):
    print(
        """

 /$$   /$$                                                    /$$$$$$  /$$$$$$
| $$  | $$                                                   /$$__  $$|_  $$_/
| $$  | $$  /$$$$$$  /$$$$$$/$$$$   /$$$$$$   /$$$$$$       | $$  \__/  | $$  
| $$$$$$$$ |____  $$| $$_  $$_  $$ /$$__  $$ /$$__  $$      | $$        | $$  
| $$__  $$  /$$$$$$$| $$ \ $$ \ $$| $$$$$$$$| $$  \ $$      | $$        | $$  
| $$  | $$ /$$__  $$| $$ | $$ | $$| $$_____/| $$  | $$      | $$    $$  | $$  
| $$  | $$|  $$$$$$$| $$ | $$ | $$|  $$$$$$$|  $$$$$$$      |  $$$$$$/ /$$$$$$
|__/  |__/ \_______/|__/ |__/ |__/ \_______/ \____  $$       \______/ |______/
                                             /$$  \ $$                        
                                            |  $$$$$$/                        
                                             \______/                         """
    )
    print("all devices: ")

    if debug:
        hameg_device_handle = Hameg3010DeviceMock()
    else:
        dev = usb.core.find(find_all=True)

        # loop through devices, printing vendor and product ids in decimal and hex

        no_devices_found = 0
        for cfg in dev:
            no_devices_found += 1
            print(f"Decimal VendorID= {cfg.idVendor} ProductID= {cfg.idProduct}")
            print(
                f"Hexadecimal VendorID= {hex(cfg.idVendor)} ProductID= {hex(cfg.idProduct)}"
            )
        print(f"no devices found: {no_devices_found}")
        hameg_device_handle = Hameg3010Device.connect_using_vid_pid(
            id_vendor=0x403, id_product=0xED72
        )

    print(
        f"""
    Connected to Hameg device
    IDN              : {hameg_device_handle.send_await_resp("*IDN?")[1][2:-1]}
    Software Version : {hameg_device_handle.send_await_resp("SYSTem:SOFTware?")[1][2:-1]}
    Hardware Version : {hameg_device_handle.send_await_resp("SYSTem:HARDware?")[1][2:-1]}
              """
    )
    # clean errors
    hameg_device_handle.send_await_resp("SYSTem:ERRor:ALL?")
    return hameg_device_handle


if __name__ == "__main__":
    hameg_device_handle = set_up_hamed_device(debug=False)
    hameg_console_loop(hameg_device_handle)
