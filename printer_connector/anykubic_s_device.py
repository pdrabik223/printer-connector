
import time
from typing import Any, Tuple
from serial import Serial
import logging
from exceptions import ConnectionFailed

class AnycubicSDevice:
    _device: Serial = None  # pyserial connector device

    def __init__(self, device) -> None:
        self._device = device
    def __del__(self): 
        self._device.close()
        
    @staticmethod
    def connect_on_port(port: str, baudrate: int = 115200, timeout = 10) -> "AnycubicSDevice":
        dev = AnycubicSDevice(device=Serial(port=port, baudrate=baudrate, timeout=timeout))
        time.sleep(2)
        
        resp =  str([chr(val) for val in dev._device.readline()][2:-3])
        
        while(resp != []):
            print(resp)
            time.sleep(0.2)
            resp  = str([chr(val) for val in dev._device.readline()][2:-3])
                    
        return dev

        
    def send(self, command) -> str:
        return send_and_await_resp(device=self._device, message=self.csline(command))
    
    def checksum(self,line):
        cs = 0
        for i in range(0,len(line)):
            cs ^= ord(line[i]) & 0xff
        cs &= 0xff
        return str(cs)
    
    def csline(self,line):
        return line+"*"+self.checksum(line)