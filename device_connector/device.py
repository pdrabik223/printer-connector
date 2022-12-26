
import serial.tools.list_ports
def static_vars(**kwargs)->callable:
    
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate

    
def list_available_serial_ports():
    
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
            print("{}: {} [{}]".format(port, desc, hwid))


class Device:
    """
    **Base class for various printer devices.** 
    """
    def send_and_await(command: str) -> str:
        """
        **Send command and await response.**
        Depending on used software, response might be returned as soon as command is acknowledged by the device, or after completion.
        Function will block thread and wait for response, after predefined tine function will return received message or 'no message received' error.

        Parameters
        ----------
        **command : str**
            Command send to device 

        Returns
        ------- 
        **str**
            Response from device
        """
        pass
    
    def connect_on_port(port: str, baudrate: int = 250000, timeout:int=5)->"Device":
        """
        **Connects to device on specified port.** 

        Parameters
        ----------
        **port : str**
            Port on witch Printer device is connected
        
        **baudrate : int, optional**
            Information transfer speed (in bits per second), **by default 250000**
        
        **timeout : int, optional**
            Await for response time in seconds, **by default 5**

        Returns
        -------
        **Device**
           Correctly set up connector to printer device
        """
        pass

    def connect()->"Device":
        """
        **Search for port on which printed device is connected to pc.**
        If none is found, error is raised.  

        Returns
        -------
        **Device**
            Correctly set up connector to printer device.
        """
        pass