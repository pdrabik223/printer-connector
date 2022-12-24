class Device:
    def send_and_await(command: str) -> str:
        pass
    
    def connect_on_port(port: str, baudrate: int = 250000, timeout:int=5)->"Device":
        pass

    def connect()->"Device":
        pass