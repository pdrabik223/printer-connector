import time
from serial import Serial

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


if __name__ == "__main__":
    printer = PrusaDevice.connect_on_port("COM9", 115200)

    commands  = [
    'M201 X1000 Y1000 Z200 E5000' ,
    'M203 X200 Y200 Z12 E120',
    'M204 P1250 R1250 T1250',
    'M205 X8.00 Y8.00 Z0.40 E4.50',
    'M205 S0 T0',
    'M107',
    'M862.3 P "MK3S"',
    'M862.1 P0.4',
    'G90',
    'G28 W',
    ]
    for command in commands:
        printer.send_and_await(command=command)
        
    printer.send_and_await("G1 Z40 Y60")
        