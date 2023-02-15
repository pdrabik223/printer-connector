"""@package pocketvna
taking LMR16 calibration file and saving standards and raw-measurements
then skrf_LMR16_calibration.py would be used to calibrate over these standards
# @file
#  @defgroup API pocketVna API
"""


import skrf
import numpy
import pocketvna

driver = pocketvna.Driver()

print("***********  -=LMR16=- ***************")
print("I see {} device(s)".format(driver.count()))

## Pay attention: safe_connect_to returns True on success, False on connection error (victim is the driver or the device) and None -- on unknown error
if driver.safe_connect_to(0) != True:
    print("No device")
    exit()

z0 = driver.Z0()

start, end, steps = 1000000, 100000000, 100

freq = numpy.linspace(start, end, steps, dtype=numpy.uint64)

print("Device: {}, Characteristic Impedance: {}".format(driver.devinfo(), z0))
print("SCAN: [{}; {}] / {}".format(start, end, steps))
print(
    "This script takes LMR16 Calibration Standards and Measurement. This is done to guaranty all standards and measurements to have the same frequency"
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
def take_through():
    print("THROUGH")

    raw_input(
        "Connect P1 with P2 with LINE and Press Enter to Take FULL trugh measurements: "
    )
    ntwrk = get_network(freq)

    ntwrk.write_touchstone(filename="calibration_data_lmr16/through.s2p")
    print("Through measurements are stored into calibration_data_lmr16/through.s2p")


def take_reflect_reflect_separately():
    print("Reflect-Reflect is scanned separately")

    raw_input("Connect REFLECT (Short) to Port-1 and Press Enter: ")
    s11_load, s21_load = scan_s11_s21(freq)

    raw_input("Connect REFLECT (Short) to Port-2 and Press Enter: ")
    s22_load, s12_load = scan_s22_s12(freq)

    ntwrk = build_network_full(freq, s11_load, s21_load, s12_load, s22_load, z0)

    ntwrk.write_touchstone(filename="calibration_data_lmr16/lmr16-reflect-reflect.s2p")

    print("calibration_data_lmr16/lmr16-reflect-reflect.s2p is stored")


def take_match_match_separately():
    print("Match-Match is scanned separately")

    raw_input("Connect MATCH (Load) to Port-1 and Press Enter: ")
    s11_load, s21_load = scan_s11_s21(freq)

    raw_input("Connect MATCH (Load) to Port-2 and Press Enter: ")
    s22_load, s12_load = scan_s22_s12(freq)

    ntwrk = build_network_full(freq, s11_load, s21_load, s12_load, s22_load, z0)

    ntwrk.write_touchstone(filename="calibration_data_lmr16/lmr16-match-match.s2p")

    print("calibration_data_lmr16/match_match.s2p is stored")


def take_match_reflect():
    print("Match-Reflect is scanned separately")

    raw_input(
        "Connect MATCH (load) to Port-1 and REFLECT (short) to Port-2 and Press Enter: "
    )
    ntwrk = get_network(freq)

    ntwrk.write_touchstone(filename="calibration_data_lmr16/lmr16-match-reflect.s2p")
    print(
        "Through measurements are stored into calibration_data_lmr16/lmr16-match-reflect.s2p"
    )


def take_reflect_match():
    print("Reflect-Match is scanned separately")

    raw_input(
        "Connect REFLECT (short) to Port-1 and MATCH (load) to Port-2 and Press Enter: "
    )
    ntwrk = get_network(freq)

    ntwrk.write_touchstone(filename="calibration_data_lmr16/lmr16-reflect-match.s2p")
    print(
        "Through measurements are stored into calibration_data_lmr16/lmr16-reflect-match.s2p"
    )


def take_measurements():
    raw_input("Connect DUT device and Press Enter to Take Raw Measurements:")
    ntwrk = get_network(freq)
    ntwrk.write_touchstone(filename="calibration_data_lmr16/meas.s2p")


take_through()

take_reflect_reflect_separately()

take_match_match_separately()

take_reflect_match()

take_match_reflect()

take_measurements()


driver.close()
pocketvna.close_api()
