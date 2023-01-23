import time

from printer_device_connector.device import Device, static_vars


class PrinterDeviceMock(Device):
    def send_and_await(self, command: str) -> str:
        if "G1" in command:
            self.set_current_position_from_string(command)
            time.sleep(0.5)

        elif "G28" in command:
            self.current_position.from_tuple((0, 0, 0))
            time.sleep(1)

        return "this is mock"

    def connect_on_port(
            port: str, baudrate: int = 250000, timeout: int = 5
    ) -> "PrinterDeviceMock":
        print(f"Connected on port: '{69}', desc: 'table', hwid: 'kazooooo")
        return PrinterDeviceMock()

    @staticmethod
    def connect() -> "PrinterDeviceMock":
        print(f"Connected on port: '{69}', desc: 'table', hwid: 'kazooooo")
        return PrinterDeviceMock()

    def startup_procedure(self) -> None:
        pass
