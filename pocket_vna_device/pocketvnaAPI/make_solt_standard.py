"""@package pocketvna
taking SOLT(tosm) calibration file and saving standards

then skrf_solt_calibration.py would be used to calibrate over these standards
# @file
#  @defgroup API pocketVna API
"""

import skrf
import numpy
import pocketvna

driver = pocketvna.Driver()

print("I see {} device(s)".format(driver.count()))

## Pay attention: safe_connect_to returns True on success, False on connection error (victim is the driver or the device) and None -- on unknown error
if driver.safe_connect_to(0) != True:
    print("No device")
    exit(666)

z0 = driver.Z0()

start, end, steps = 1000000, 100000000, 100

freq = numpy.linspace(start, end, steps, dtype=numpy.uint64)

print("Device: {}, Characteristic Impedance: {}".format(driver.devinfo(), z0))
print("SCAN: [{}; {}] / {}".format(start, end, steps))
print(
    "This script takes Calibration Standards and Measurement. This is done to guaranty all standards and measurements to have the same frequency"
)


def get_network(freq):
    return driver.scan_skrf_network(freq, 10)


def build_network_full(freq, s11, s21, s12, s22, z0):
    s = numpy.zeros((len(freq), 2, 2), dtype=numpy.complex128)

    s[:, 0, 0], s[:, 0, 1] = s11, s12
    s[:, 1, 0], s[:, 1, 1] = s21, s22

    ntwk = skrf.Network()
    ntwk.s = s
    ntwk.frequency = skrf.Frequency.from_f(freq, unit="hz")
    ntwk.z0 = z0

    return ntwk


def build_network(freq, s11, s22, z0):
    s = numpy.zeros((len(freq), 2, 2), dtype=numpy.complex128)

    for i in range(0, len(freq)):
        s[i, 0, 0], s[i, 0, 1] = s11[i], 0.0 + 0j
        s[i, 1, 0], s[i, 1, 1] = 0.0 + 0j, s22[i]

    ntwk = skrf.Network()
    ntwk.s = s
    ntwk.frequency = skrf.Frequency.from_f(freq, unit="hz")
    ntwk.z0 = z0

    return ntwk


def build_network_th(freq, s21, s12, z0):
    s = numpy.zeros((len(freq), 2, 2), dtype=numpy.complex128)

    for i in range(0, len(freq)):
        s[i, 0, 0], s[i, 0, 1] = 0.0, s12[i]
        s[i, 1, 0], s[i, 1, 1] = s21[i], 0.0

    ntwk = skrf.Network()
    ntwk.s = s
    ntwk.frequency = skrf.Frequency.from_f(freq, unit="hz")
    ntwk.z0 = z0

    return ntwk


def scan_s11(freq):
    s11, s21, s12, s22 = driver.scan(freq, 10, pocketvna.NetworkParams.S11)
    return s11


def scan_s11_s21(freq):
    s11, s21, s12, s22 = driver.scan(freq, 10, pocketvna.NetworkParams.PORT1)
    return s11, s21


def scan_s22_s12(freq):
    s11, s21, s12, s22 = driver.scan(freq, 10, pocketvna.NetworkParams.PORT2)
    return s22, s12


def scan_s22(freq):
    s11, s21, s12, s22 = driver.scan(freq, 10, pocketvna.NetworkParams.S22)
    return s22


def scan_s11_n_s22_open(freq):
    s11, s21, s12, s22 = driver.scan(freq, 10, pocketvna.NetworkParams.REFL)
    return s11, s22


## ----------------------------------------------------------------


def take_short_short():
    print(
        "Short S11 and S22 is scanned separately. So script supports one-standard kit only"
    )

    raw_input("Connect SHORT to Port-1 and Press Enter to Take S11 short: ")
    s11_short = scan_s11(freq)

    raw_input("Connect SHORT to Port-2 and Press Enter to Take S22 short: ")
    s22_short = scan_s22(freq)

    ntwrk = build_network(freq, s11_short, s22_short, z0)

    ntwrk.write_touchstone(filename="short_short.s2p")

    print("short_short.s2p is stored")


def take_open_open():
    print(
        "Open S11 and S22 is scanned separately. So script supports one-standard kit scan only"
    )

    raw_input("Connect OPEN to Port-1 and Press Enter to Take S11 open: ")
    s11_open = scan_s11(freq)

    raw_input("Connect OPEN to Port-2 and Press Enter to Take S22 open: ")
    s22_open = scan_s22(freq)

    ntwrk = build_network(freq, s11_open, s22_open, z0)

    ntwrk.write_touchstone(filename="open_open.s2p")

    print("open_open.s2p is stored")


def take_load_load():
    print(
        "Load S11 and S22 is scanned separately. So script supports one-standard kit scan only"
    )

    raw_input("Connect LOAD to Port-1 and Press Enter to Take S11 Load: ")
    s11_load, s21_load = scan_s11_s21(freq)

    raw_input("Connect LOAD to Port-2 and Press Enter to Take S22 Load: ")
    s22_load, s12_load = scan_s22_s12(freq)

    ntwrk = build_network_full(freq, s11_load, s21_load, s12_load, s22_load, z0)

    ntwrk.write_touchstone(filename="load_load.s2p")

    print("load_load.s2p is stored")


def take_through():
    raw_input("Connect P1 with P2 and Press Enter to Take FULL trugh measurements: ")
    ntwrk = get_network(freq)

    ntwrk.write_touchstone(filename="through.s2p")
    print("Through measurements are stored into TRUE_2P_Through.s2p")


def take_measurements():
    raw_input("Connect DUT device and Press Enter to Take Raw Measurements:")
    ntwrk = get_network(freq)
    ntwrk.write_touchstone(filename="meas.s2p")


take_short_short()

take_open_open()

take_load_load()

take_through()

take_measurements()


driver.close()
pocketvna.close_api()
