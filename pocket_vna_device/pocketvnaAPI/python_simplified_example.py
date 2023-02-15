import pocketvna
import math

## Example for simplified connection. Using C-API

MAX_ATTEMPT_COUNT = 10
AVERAGE = 5
CALLBACK = None


def open_device():
    device_handler = None

    for attempt in range(0, MAX_ATTEMPT_COUNT):
        device_handler = pocketvna.get_first_available_device_handler()
        if device_handler is not None:
            break

    return device_handler


try:
    device_handler = open_device()

    if device_handler is not None:
        print("Device is opened")

        frequencies = [1000000, 2000000, 3000000]
        s11 = None

        ## This condition is just an example. It is v
        # if NUMPY is not None:
        #    s11, s21, s12, s22 = pocketvna.scan_frequencies(device_handler, frequencies, AVERAGE, pocketvna.NetworkParams.S11, CALLBACK)
        # else:
        #    s11, s21, s12, s22 = pocketvna.scan_frequencies_no_numpy(device_handler, frequencies, AVERAGE, pocketvna.NetworkParams.S11, CALLBACK)

        # for simplicity use without NumPy. Thus s11 (and s21, s12, s22) are python list (not numpy's arrays)
        s11, s21, s12, s22 = pocketvna.scan_frequencies_no_numpy(
            device_handler, frequencies, AVERAGE, pocketvna.NetworkParams.S11, CALLBACK
        )

        print("S11: ", s11)
        print("S21: ", s21)
        print("S12: ", s12)
        print("S22: ", s22)

        pocketvna.release_handler(device_handler)
    else:
        print("No device")

finally:
    ## It would be nice if you do not forget to call it. But it is not so necessary :)
    pocketvna.close_api()
