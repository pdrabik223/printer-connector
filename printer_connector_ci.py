from g_code_file_handler.g_code_file import GCodeFile
from configs.exceptions import EndofFile
from printer_connector.prusa_device import AnycubicDevice
import time


def print_from_file(printer: AnycubicDevice, file: GCodeFile) -> None:
    print("Commencing Printing.")
    while True: 
        try:
            command = file.next_gcode_command()

            print(command)
            printer.send((command))            

        except EndofFile as ex:
            print("Printing completed.")
            return None


if __name__ == "__main__":
    printer = AnycubicDevice.connect_on_port("COM10", 115200)

    time.sleep(2)
    print(printer.send('M115 U'))
    print(printer.send('M115 U'))
    print(printer.send('M115 U'))
    print(printer.send('M105'))    
