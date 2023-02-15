#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pocketvna
import math
from sys import exit

## Getting version: v is version and pi is 3.14.. number
v, pi = pocketvna.driver_version()

## Optional: set LogLevel
pocketvna.set_driver_option(
    pocketvna.DriverOptionsEnum.LogLevel,
    pocketvna.DriverOptionsEnum.LogLevelsEnum.debug,
)

print("pocketvna.driver_version() => VERSION: {}, PI: {}".format(v, pi))

## Create Driver Instance.
## If something went wrong with API it raises Exceptions PocketVnaError
driver = pocketvna.Driver()

## Check how many devices are detected
## If 'count' is 0, you can call driver.enumerate() to check it again
print("Driver is created: {} devices connected..".format(driver.count()))
for i in range(0, driver.count()):
    print("Device {}".format(i))
    print("\t {}".format(driver.info_at(i)))

if driver.count() < 1:
    print("No device is detected. Connect and call enumerate() again")
    exit(1)

## Let's connect to a first one. connect_to returns Either True or raises an Exception.
## You can use safe_connect_to(index) which returns True/False/None. None in case of Exception is raised
# if not driver.connect_to(0):
#    print('Failed to connect')
#    exit(2)

# Alternative to connect_to(index) is connect_to_first(interface_code)
if not driver.connect_to_first(pocketvna.ConnectionInterfaceCode.CIface_HID):
    print("Failed to connect HID")
    exit(21)


## This function checks whether new connection is valid
## Connection can be invalid if device is disconnected
if not driver.valid():
    print("Looks kind of driver is open but invalid. Disconnected?")
    exit(3)

## In most cases, if device is disconnected during any call PocketVnaHandlerInvalid exception is raised
try:
    print("TEST REQUST: ")

    ## START TEST SECTION. YOU do not need it!!
    ## Example of test request. Usually you do not need to call it!!! It is for debug purposes
    r, s = driver.test_req()

    print(" ".join(["%02x " % x for x in r]).strip(), "x", s)

    test_is_ok = r[0] == 0 and r[7] == 0x0D and r[4] == 0x0D
    if not test_is_ok:
        print("BAD TEST RESULT!!")
        print("")
    else:
        ## test_req fills Device Internal Buffer with sequence 0, 1, 2, 3, 4... (i % 256)
        ## Let's check. Again you do not have to call it!!! It is for debug purposes
        r, s = driver.read_internal_buffer()
        print(" ".join(["%02x " % x for x in r]).strip(), "x", s)
    ## END TEST SECTION. YOU do not need it!!

    ## LETS CHECK supported S Parameters
    ## Elder devices support S11/S21 parameters only
    nps = ""
    if driver.has_s11():
        nps = nps + " S11 "
    if driver.has_s21():
        nps = nps + " S21 "
    if driver.has_s12():
        nps = nps + " S12 "
    if driver.has_s22():
        nps = nps + " S22 "

    ## FIRMWARE VERSION ON THE DEVICE
    firmware_version = driver.version()

    print("\tSupports: {}, Firmware: {}".format(nps, firmware_version))

    ## GET Characteristic Impedance (Zero Resistance/Impedance; Reference Impedance/Resistance).
    ## Usually it is 50Ohms
    RR = driver.Z0()

    ## Get valid frequency range. Usually [1_Hz; 6_GHz]. It is a range which device can handle
    ## It may be some boundaries are not processed correctly. For example scan for 1KHz may be not Good
    start, end = driver.valid_frequency_range()

    print("\tZ0: {}; range [{}; {}]".format(RR, start, end))

    ## Get working frequency. Usually [100_KHz; 6 GHz]. It is a range device claims to process correctly
    start, end = driver.reasonable_frequency_range()
    print("\tWork Frequency: [{}; {}]".format(start, end))

    ## Ok. You know everything. You have connected with a device. Let's scan. For single Frequency

    ## Pay attention on average value passing. It tells how many times device takes measurements and then average them
    ## In case average is 10. Device takes 10 measurements, sum them up, and devides by 10th
    ## ANYWAY you receive just S-Parameter, you do not have to process it somehow. More average value more precise value
    ## But it takes a time and may cause device bad response. Allowed values between 1 and 10000, but it is better to use bellow 100
    average = 10

    ## single_scan returns 4 complex S-Parameters: s11, s21, s12, s22.
    ## Non requested values are filled with Zeros

    print("1 GHz FULL Scan (S11, S21, S12, S22 parameters): ")
    s11, s21, s12, s22 = driver.single_scan(
        1000000000, average, pocketvna.NetworkParams.ALL
    )
    print("\t{};\t\t{};\n\t{};\t\t{};".format(s11, s21, s12, s22))

    print("1 GHz S11-Only Scan (1 average): ")
    s11, s21, s12, s22 = driver.single_scan(1000000000, 1, pocketvna.NetworkParams.S11)
    print("\t{};\t\t{};\n\t{};\t\t{};".format(s11, s21, s12, s22))

    print("2 GHz S21-Only Scan (100 average): ")
    s11, s21, s12, s22 = driver.single_scan(
        2000000000, 100, pocketvna.NetworkParams.S21
    )
    print("\t{};\t\t{};\n\t{};\t\t{};".format(s11, s21, s12, s22))

    print("3 GHz S12-Only Scan (10 average): ")
    s11, s21, s12, s22 = driver.single_scan(3000000000, 10, pocketvna.NetworkParams.S12)
    print("\t{};\t\t{};\n\t{};\t\t{};".format(s11, s21, s12, s22))

    print("4 GHz S22-Only Scan: ")
    s11, s21, s12, s22 = driver.single_scan(4000000000, 10, pocketvna.NetworkParams.S22)
    print("\t{};\t\t{};\n\t{};\t\t{};".format(s11, s21, s12, s22))

    ## Now a scan for a set of frequencies

    ## Prepare frequencies. You can distribute them linearly, logarithmically or some other way
    print("Frequency Vector Request:")
    num_of_points = 2
    freq = [(10000000 * i) for i in range(1, num_of_points + 1)]

    ## Very similar to single_scan but accepts an array of frequencies, not single frequency
    ## Returns arrays of complex S-Parameters: S11, S21, S12, S22
    ## S-Parameters arrays will be of the same type as freqency array
    ## Non-requested parameters are filled with Zeros (0 + 0i)
    ## Last (3rd) parameter may be on listed in pocketvna.NetworkParams
    ##    -> pocketvna.NetworkParams.AllSupported -> all supported by device
    ##    -> pocketvna.NetworkParams.ALL          => ask all S11|S21|S12|S22
    ##    -> pocketvna.NetworkParams.S21          => S21 only
    ##    -> (pocketvna.NetworkParams.S21 | pocketvna.NetworkParams.S11) => S21 and S11
    ##    -> pay attention this function returns 4 numpy arrays. If no numpy library then it returns native python list
    s11, s21, s12, s22 = driver.scan(freq, 10, pocketvna.NetworkParams.AllSupported)

    ## PRINT SCANNED VALUES
    print("SCANNED FREQUENCY VECTOR: ")
    for i in range(0, len(freq)):
        print(freq[i])
        print("\t{};\t\t{}".format(s11[i], s21[i]))
        print("\t{};\t\t{}".format(s12[i], s22[i]))

    print("CLOSING DRIVER:")

    ## Let's check if API returns complex numbers correctly
    ## Use debugscan which:
    ##*  Fills p1 using pattern ( i -- zerobased index )
    ##*       p1[i].real = Pi / (i+1)
    ##        p1[i].imag = 1. / p1[i].real
    ##        p2[i].real = Pi * i
    ##        p2[i].imag = Pi ** (i+1)
    print("\nCheck debugscan\n")
    num_of_points = 5
    p1, p2 = driver.debugscan(num_of_points)
    for i in range(0, num_of_points):
        print(
            "P1 Expected: ("
            + str(math.pi / (i + 1))
            + "; "
            + str(1.0 / (math.pi / (i + 1)))
            + "j)\t"
        )
        print("   REAL: (" + str(p1[i].real) + "; " + str(p1[i].imag) + "i)\n")

        print(
            "P2 Expected: ("
            + str(math.pi * i)
            + "; "
            + str((math.pi ** (i + 1)))
            + "j)\t"
        )
        print("   REAL: (" + str(p2[i].real) + "; " + str(p2[i].imag) + "i)\n")

    ## Close Connection. After this you can re-enumerate it and open another one
    ##  like driver.enumerate()
    ##  if driver.count() > 0: driver.connect_to(0)
    driver.close()

except pocketvna.PocketVnaHandlerInvalid:
    ## Very Probably Device is disconnected
    print("Looks kind of device is disconnected ( or dead ;) )")

    print("\n. **** THE END ***************")

finally:
    ## It would be nice if you do not forget to call it. But it is not so necessary :)
    pocketvna.close_api()
