import serial.tools.list_ports

if __name__ == "__main__":
    available_ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(available_ports):
        print(f"Scanning port: '{port}', desc: '{desc}', hwid: '{hwid}")
