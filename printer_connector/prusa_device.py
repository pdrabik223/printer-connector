import time
from typing import Any, Tuple
from serial import Serial
import logging
from exceptions import ConnectionFailed

# def send_and_await_resp(device: Serial, message: str) -> str:
#     if message[-1] != '\n':
#         message += '\n'
        
#     device.write(bytearray(message, 'utf-8'))
#     raw_resp = str(device.readline())     
#     return (raw_resp,raw_resp[2:-3]) 


class PrusaDevice:
    _device: Serial = None  # pyserial connector device

    def __init__(self, device) -> None:
        self._device = device

    @staticmethod
    def connect_on_port(port: str, baudrate: int = 115200, timeout = 5) -> "PrusaDevice":
        dev = PrusaDevice(device=Serial(port=port, baudrate=baudrate, timeout=timeout))
        time.sleep(2)
        
        resp = dev._device.readline().decode('utf-8')
        while(resp != ''):
            print(resp)
            resp = dev._device.readline().decode('utf-8')

        
        return dev
    
    def send_and_await(self, command) -> str:
        if command[-1] != '\n':
            command += '\n'
        
        self._device.write(bytearray(command, 'utf-8'))
        resp = ""
        while('ok' not in resp):
            resp = str(self._device.readline().decode('utf-8'))
            print(resp)
             
    
    # @staticmethod
    # def checksum(line):
    #     cs = 0
    #     for i in range(0,len(line)):
    #         cs ^= ord(line[i]) & 0xff
    #     cs &= 0xff
    #     return str(cs)
    
    # @staticmethod
    # def csline(line):
    #     return line+"*"+PrusaDevice.checksum(line)
    
if __name__ == "__main__":
    printer = PrusaDevice.connect_on_port("COM9", 115200)

    print("sending message")
    while(True):
        print(printer.send_and_await('G28 W'))
        print("sleep")
        time.sleep(4)
        print("re sending")
