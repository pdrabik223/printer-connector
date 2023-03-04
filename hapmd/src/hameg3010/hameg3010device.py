from typing import Tuple
import usb.core
import usb.util
import logging


class Hameg3010Device:
    def __init__(self, device_handle: usb.core.Device) -> None:
        self.device_handle: usb.core.Device = device_handle
        self.device_handle.set_configuration()

    @staticmethod
    def connect_using_vid_pid(id_vendor: int, id_product: int) -> "Hameg3010Device":
        logging.debug(f"connecting do device with pid: {id_product}, vid: {id_vendor}")

        device = usb.core.find(idVendor=id_vendor, idProduct=id_product)
        # device = usb.core.
        if device is None:
            raise ValueError(
                f"Device is not found vid: {hex(id_vendor)} pid: {hex(id_product)}"
            )

        logging.debug(
            f"connected do device with vid: {hex(id_vendor)} pid: {hex(id_product)}"
        )
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
            self.device_handle.write(0x2, command)
        except Exception:
            logging.error(f"error occurred while writing to device", exc_info=True)
            raise

    def _await_resp(self):
        resp = self.device_handle.read(0x81, 1_000_000, 1_000)

        # Following lines are hack
        # problem seems to be that after sending message multiple readout are required to get response
        # the delay between readouts is not important, can be as short as 0.1 s
        # seems like a problem with buffer somewhere, following while statement waits for non-empty readout
        # thus avoiding the issue, this will come back tho
        # TODO find the source of this problem

        counter = 0
        while len(resp) == 2:
            resp = self.device_handle.read(0x81, 1_000_000, 1_000)
            # print(resp)
            counter += 1
            if counter > 10:
                break

        try:
            return (resp, bytearray(resp).decode("utf-8"))

        except Exception as ex:
            return (resp, f"fail with error message: {str(ex)}")

    def send_await_resp(self, cmd: str) -> Tuple[bytearray, str]:
        # print(f"req:  {cmd}")
        if len(cmd) != 0:
            self._send_str(command=cmd)

        resp, decoded = self._await_resp()
        # print(f"resp: {resp}")
        return (resp, decoded)
