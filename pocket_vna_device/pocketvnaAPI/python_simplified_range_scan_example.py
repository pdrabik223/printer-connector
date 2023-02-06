import pocketvna
import math

import signal
import sys

## Example for simplified connection. Using C-API

class Settings:
    startFreq, endFreq = 1000000, 32000000
    steps = 1000
    MAX_ATTEMPT_COUNT = 10
    AVERAGE = 2
    NetworkParameters = pocketvna.NetworkParams.S11

    interruptFlag = False
    useNumpy=True

def progress_callback(handle,index):
    print( " __" + str(index * 100 / Settings.steps) + "%\r")
    return pocketvna.Continue if not Settings.interruptFlag else pocketvna.Cancel

def open_device():
    device_handler = None

    for attempt in range(0, Settings.MAX_ATTEMPT_COUNT):
       device_handler = pocketvna.get_first_available_device_handler()
       if device_handler is not None:
           break

    return device_handler

def send_cancel_scan(sig, frame):
    global interruptFlag
    print('You pressed Ctrl+C!. Canceling scan...\n')
    Settings.interruptFlag = True
        
signal.signal(signal.SIGINT, send_cancel_scan)

try:
    device_handler = open_device()

    if device_handler is not None:
        print("Device is opened")

        ## This condition is just an example. It is v
        try:
            if Settings.useNumpy and pocketvna.NUMPY:
                print("Numpy Version\n")
                # for simplicity use without NumPy. Thus s11 (and s21, s12, s22) are python list (not numpy's arrays)
                s11, s21, s12, s22 = pocketvna.scan_frequencies_for_range(device_handler, 
                    Settings.startFreq, Settings.endFreq, Settings.steps, pocketvna.Distributions.Linear, 
                    Settings.AVERAGE, Settings.NetworkParameters, 
                    progress_callback
                )
            else:
                print("non-Numpy (python list) Version\n")
                # for simplicity use without NumPy. Thus s11 (and s21, s12, s22) are python list (not numpy's arrays)
                s11, s21, s12, s22 = pocketvna.scan_frequencies_for_range_no_numpy(device_handler, 
                    Settings.startFreq, Settings.endFreq, Settings.steps, pocketvna.Distributions.Linear, 
                    Settings.AVERAGE, Settings.NetworkParameters, 
                    progress_callback
                )

            print("S11: ", s11)
            print("S21: ", s21)
            print("S12: ", s12)
            print("S22: ", s22)

        except pocketvna.PocketVnaScanCanceled:
            print("Scan is canceled manually")
       

        pocketvna.release_handler(device_handler)
    else:
        print("No device")

finally:
    ## It would be nice if you do not forget to call it. But it is not so necessary :)
    pocketvna.close_api()
