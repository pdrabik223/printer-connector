import time
from serial import Serial

class PrusaDevice:
    _device: Serial = None  # pyserial connector device

    def __init__(self, device) -> None:
        self._device = device

    @staticmethod
    def connect_on_port(port: str, baudrate: int = 115200, timeout = 5) -> "PrusaDevice":
        """
        Connect to Prusa device
        Args:
            port (str): COM port on windows system, usually 9.
            baudrate (int, optional): baudrate. Defaults to 115200.
            timeout (int, optional): timeout. Defaults to 5.

        Returns:
            PrusaDevice: _description_
        """
        dev = PrusaDevice(device=Serial(port=port, baudrate=baudrate, timeout=timeout))
        time.sleep(2)
        
        resp = dev._device.readline().decode('utf-8')
        
        while(resp != ''):
            print(resp)
            resp = dev._device.readline().decode('utf-8')
        
        return dev
    
    def send_and_await(self, command:str) -> str:
        """
        send command to Prusa device, than await response

        Args:
            command (str): g-code command

        Returns:
            str: response from device
        """
        if command[-1] != '\n':
            command += '\n'
        
        self._device.write(bytearray(command, 'utf-8'))
        
        resp = ""
        # after every successfully completed command, prusa returns 'ok' message 
        while('ok' not in resp):
            resp = str(self._device.readline().decode('utf-8'))


    def startup_procedure(self)->None:
        """
        send default parameters (motor speed, acceleration, model check, etc...) 
        and zero all the axies  
        """
        commands  = [
        'M201 X1000 Y1000 Z200 E5000' ,
        'M203 X200 Y200 Z12 E120',
        'M204 P1250 R1250 T1250',
        'M205 X8.00 Y8.00 Z0.40 E4.50',
        'M205 S0 T0',
        'M107',
        'M862.3 P "MK3S"',
        # 'M862.1 P0.4',
        'G90',
        'G28 W',
        ]
        for command in commands:
            printer.send_and_await(command=command)
            
import keyboard
if __name__ == "__main__":
    printer = PrusaDevice.connect_on_port("COM9")

    printer.startup_procedure()
    
    x = 0.0
    y = 0.0
    z = 0.0
    
    change = 1
    
    while(True):
        try:
            if keyboard.is_pressed('a'): 
                x-=change
            elif keyboard.is_pressed('d'): 
                x+=change
                
            if keyboard.is_pressed('w'): 
                z+=change
            elif keyboard.is_pressed('s'): 
                z-=change
                
            if keyboard.is_pressed('q'): 
                y+=change
            elif keyboard.is_pressed('e'): 
                y-=change
                
            if keyboard.is_pressed('r'): 
                change+= 1
                
            elif keyboard.is_pressed('f'): 
                if change>1:
                    change-=1
        except:
            pass 
        printer.send_and_await(command=f"G1 X{x} Y{y} Z{z}")
        