import time

from device_connector.device import Device, static_vars


class DeviceMock(Device):
    def send_and_await(self, command: str) -> str:
        if "G1" in command:
            time.sleep(0.5)

        elif "G28" in command:
            time.sleep(1)

        return 'this is mock'

    def connect_on_port(
            port: str, baudrate: int = 250000, timeout: int = 5
    ) -> "DeviceMock":
        print(f"Connected on port: '{69}', desc: 'table', hwid: 'kazooooo")
        return DeviceMock()

    @staticmethod
    def connect() -> "DeviceMock":
        print(f"Connected on port: '{69}', desc: 'table', hwid: 'kazooooo")
        return DeviceMock()

    def startup_procedure(self) -> None:
        pass
