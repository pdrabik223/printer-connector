import pocketvnaAPI.pocketvna
from pocketvnaAPI.pocketvna import *


def close():
    pocketvnaAPI.pocketvna.close_api()


class PocketVnaDevice:

    def __init__(self):
        print(f"pocketvnaAPI Version: {pocketvnaAPI.pocketvna.driver_version()}")
        self.driver = pocketvnaAPI.pocketvna.Driver()
        print("")
        print("List all available self.drivers:")
        for i in range(0, self.driver.count()):
            print('Device {}'.format(i))
            print('\t {}'.format(self.driver.info_at(i)))

        self.driver.connect_to_first(pocketvnaAPI.pocketvna.ConnectionInterfaceCode.CIface_HID)
        print("")
        print(f"Connected to Pocket VNA: {self.driver.valid()}")

    def scan(self, frequency=2_280_000_000, aggregate_samples=100,
             params: pocketvnaAPI.pocketvna.NetworkParams = pocketvnaAPI.pocketvna.NetworkParams.ALL):
        return complex(self.driver.single_scan(frequency, aggregate_samples, params)[0]).imag

    def __del__(self):
        close()


if __name__ == '__main__':
    vna_device = PocketVnaDevice()
    print("s11: {} (imaginary part)".format(vna_device.scan()))
