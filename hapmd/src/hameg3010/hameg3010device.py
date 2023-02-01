from typing import Any
import usb.core
import usb.util
import logging


class Hameg3010Device:
    def __init__(self, device: usb.core.Device) -> None:
        self.device: usb.core.Device = device
        self.device.set_configuration()

    @staticmethod
    def connect_using_vid_pid(idVendor, idProduct):
        logging.debug(f"connecting do device with pid: {idProduct}, vid: {idVendor}")

        device = usb.core.find(idVendor=idVendor, idProduct=idProduct)
        # device = usb.core.
        if device is None:
            raise ValueError(f"Device is not found vid: {hex(idVendor)} pid: {hex(idProduct)}")

        logging.debug(f"connected do device with vid: {hex(idVendor)} pid: {hex(idProduct)}")
        return Hameg3010Device(device)

    def _send_str(self, command: str):
        if not isinstance(command, str):
            raise TypeError(f"expected cmd to be str, received {type(command)}")

        if command is None or len(command) == 0:
            raise ValueError(f"cmd has to be not empty string, received: {command}")

        # commands send to device must end with terminal character
        if command[-1] != "\n":
            command += "\n"

        logging.debug(f"writing to device, message: {command}")

        try:
            self.device.write(0x2, command)
        except Exception:
            logging.error(f"error occurred while writing to device", exc_info=True)
            raise

    def _await_resp(self):

        resp = self.device.read(0x81, 1_000_000, 1_000)

        # Following lines are hack
        # problem seems to be that after sending message multiple readout are required to get response
        # the delay between readouts is not important, can be as short as 0.1 s
        # seems like a problem with buffer somewhere, following while statement waits for non-empty readout
        # thus avoiding the issue, this will come back tho
        # TODO find the source of this problem

        counter = 0
        while len(resp) == 2:

            resp = self.device.read(0x81, 1_000_000, 1_000)
            # print(resp)
            counter += 1
            if counter > 10:
                break

        try:
            return (resp, bytearray(resp).decode("utf-8"))

        except Exception as ex:
            return (resp, f"fail with error message: {str(ex)}")

    def send_await_resp(self, cmd: str) -> Any:
        # print(f"req:  {cmd}")
        if len(cmd) != 0:
            self._send_str(command=cmd)

        resp, decoded = self._await_resp()
        # print(f"resp: {resp}")
        return (resp, decoded)
