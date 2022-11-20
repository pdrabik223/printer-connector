
from printrun.printcore import printcore
import time


if __name__ == "__main__":
    printer=printcore('COM9', 115200)

    while not printer.online:
        "wait for printer to acknowledge connection"
        time.sleep(0.1)

    printer.send_now("M105")
    
    printer.send_now("G1 Z50")
    
    printer.disconnect()