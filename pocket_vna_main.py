import random

import pocket_vna_device.pocketvnaAPI.pocketvna as pocketvna


# from pocket_vna_device.pocketvnaAPI.pocketvna import *


def close():
    pocketvna.close_api()


class PocketVnaDevice:
    def __init__(self):
        print(f"pocketvnaAPI Version: {pocketvna.driver_version()}")
        self.driver = pocketvna.Driver()
        print("")
        print("List all available self.drivers:")
        for i in range(0, self.driver.count()):
            print("Device {}".format(i))
            print("\t {}".format(self.driver.info_at(i)))

        self.driver.connect_to_first(pocketvna.ConnectionInterfaceCode.CIface_HID)
        print("")
        print(f"Connected to Pocket VNA: {self.driver.valid()}")
        if not self.driver.valid():
            raise Exception("Device not found")

    def scan(
        self,
        frequency=int(1.32 * 10**9),
        aggregate_samples=200,
        params=pocketvna.NetworkParams.ALL,
    ):
        return self.driver.single_scan(frequency, aggregate_samples, params)[0].imag

    def __del__(self):
        close()


class PocketVnaDeviceMock:
    def __init__(self):
        print(f"pocketvnaAPI Version: (12 but I dont care, 3.141592653589793)")
        print("List all available self.drivers:\n\tmock driver")

        print("")
        print(f"Connected to Pocket VNA: Mock device")

    def scan(
        self,
        frequency=2_280_000_000,
        aggregate_samples=100,
        params: pocketvna.NetworkParams = pocketvna.NetworkParams.ALL,
    ):
        return random.random()


if __name__ == "__main__":
    vna_device = PocketVnaDevice()
    print("s11: {} (imaginary part)".format(vna_device.scan()))
    # vna_device = PocketVnaDeviceMock()
    # print("s11: {} (imaginary part)".format(vna_device.scan()))
