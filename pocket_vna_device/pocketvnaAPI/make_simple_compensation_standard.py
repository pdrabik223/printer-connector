import skrf
import numpy
import pocketvna


START = 2000 * 1000
END = 3000 * 1000
STEPS = 100
FIRMWARE_AVERAGE = 10

FREQUENCY = numpy.linspace(START, END, STEPS, dtype=numpy.uint64)

SAMPLES = len(FREQUENCY)

assert SAMPLES == STEPS, "SAMPLES should be equal to Steps: {} vs {}".format(
    SAMPLES, STEPS
)

# CALIBRATION data structure. It will be stored

# PREPARE DRIVER


driver = pocketvna.Driver()

if driver.safe_connect_to(0) != True:
    print("No device")
    exit(3)

if not driver.valid():
    print("Looks kind of deriver is open but invalid. Disconnected?")
    exit(4)

z0 = driver.Z0()

SUPPORTS_S11 = driver.has_s11()
SUPPORTS_S21 = driver.has_s21()
SUPPORTS_S12 = driver.has_s12()
SUPPORTS_S22 = driver.has_s22()

# cache skrf Frequency Object
skrfFrequency = skrf.Frequency.from_f(FREQUENCY, unit="hz")


def store_reflection_into_1p_touchstone(snn, filename):
    assert SAMPLES == len(snn), "should be equal"

    net = skrf.Network()
    net.s = snn.reshape((SAMPLES, 1, 1))
    net.frequency = skrfFrequency
    net.z0 = z0
    net.write_touchstone(filename)


def store_transmission_into_2p_touchstone(s21, s12, filename):
    assert SAMPLES == len(s21) or SAMPLES == len(s12), "should be equal"

    matrices = numpy.zeros((SAMPLES, 2, 2), dtype=numpy.complex128)

    if SUPPORTS_S21:
        matrices[:, 1, 0] = numpy.array(s21, dtype=numpy.complex128)

    if SUPPORTS_S12:
        matrices[:, 0, 1] = numpy.array(s12, dtype=numpy.complex128)

    net = skrf.Network(s=matrices, frequency=skrfFrequency, z0=z0)
    net.write_touchstone(filename)


# SHORTS
def take_short_S11():
    raw_input("Connect SHORT to Port-1. Press Enter to Take S11 short: ")
    s11, s21, s12, s22 = driver.scan(
        FREQUENCY, FIRMWARE_AVERAGE, pocketvna.NetworkParams.S11
    )

    store_reflection_into_1p_touchstone(s11, "simple_compensation_s11_short.s1p")


def take_short_S22():
    raw_input("Connect SHORT to Port-2. Press Enter to Take S22 short: ")
    s11, s21, s12, s22 = driver.scan(
        FREQUENCY, FIRMWARE_AVERAGE, pocketvna.NetworkParams.S22
    )

    store_reflection_into_1p_touchstone(s22, "simple_compensation_s22_short.s1p")


# OPEN
def take_open_S11():
    raw_input("Connect OPEN to Port-1. Press Enter to Take S11 open: ")
    s11, s21, s12, s22 = driver.scan(
        FREQUENCY, FIRMWARE_AVERAGE, pocketvna.NetworkParams.S11
    )

    store_reflection_into_1p_touchstone(s11, "simple_compensation_s11_open.s1p")


def take_open_S22():
    raw_input("Connect OPEN to Port-2. Press Enter to Take S22 open: ")
    s11, s21, s12, s22 = driver.scan(
        FREQUENCY, FIRMWARE_AVERAGE, pocketvna.NetworkParams.S22
    )

    store_reflection_into_1p_touchstone(s22, "simple_compensation_s22_open.s1p")


# LOAD
def take_load_S11():
    raw_input("Connect LOAD to Port-1. Press Enter to Take S11 load: ")
    s11, s21, s12, s22 = driver.scan(
        FREQUENCY, FIRMWARE_AVERAGE, pocketvna.NetworkParams.S11
    )

    store_reflection_into_1p_touchstone(s11, "simple_compensation_s11_load.s1p")


def take_load_S22():
    raw_input("Connect LOAD to Port-2. Press Enter to Take S22 load: ")
    s11, s21, s12, s22 = driver.scan(
        FREQUENCY, FIRMWARE_AVERAGE, pocketvna.NetworkParams.S22
    )

    store_reflection_into_1p_touchstone(s22, "simple_compensation_s22_load.s1p")


# OPEN TRANSMISION
def take_transmission_open():
    # if device supports Full 2-Port network scan, then both parameters will be taken S21 and S12
    raw_input("Leave Port-1 and Port-2 open. Press Enter to Take Transmission Open: ")
    s11, s21, s12, s22 = driver.scan(
        FREQUENCY, FIRMWARE_AVERAGE, pocketvna.NetworkParams.AllSupported
    )

    store_transmission_into_2p_touchstone(
        s21, s12, "simple_compensation_open_trans.s2p"
    )


# THRU
def take_transmission_thru():
    # if device supports Full 2-Port network scan, then both parameters will be taken S21 and S12
    raw_input(
        "Connect Port-1 and Port-2 with coaxial cable. Press Enter to Take Thru: "
    )
    s11, s21, s12, s22 = driver.scan(
        FREQUENCY, FIRMWARE_AVERAGE, pocketvna.NetworkParams.AllSupported
    )

    store_transmission_into_2p_touchstone(
        s21, s12, "simple_compensation_thru_trans.s2p"
    )


# take raw measurements
def take_raw_measurements():
    # Now, take raw data that should be calibrated
    # if device supports Full 2-Port network scan, then all parameters are taken
    # otherwise only supported(S11 and S21)
    raw_input("Connect any device to take raw measurements")
    s11, s21, s12, s22 = driver.scan(
        FREQUENCY, FIRMWARE_AVERAGE, pocketvna.NetworkParams.AllSupported
    )

    matrices = numpy.zeros((SAMPLES, 2, 2), dtype=numpy.complex128)

    if SUPPORTS_S11:
        matrices[:, 0, 0] = numpy.array(s11, dtype=numpy.complex128)

    if SUPPORTS_S21:
        matrices[:, 1, 0] = numpy.array(s21, dtype=numpy.complex128)

    if SUPPORTS_S12:
        matrices[:, 0, 1] = numpy.array(s12, dtype=numpy.complex128)

    if SUPPORTS_S22:
        matrices[:, 1, 1] = numpy.array(s22, dtype=numpy.complex128)

    net = skrf.Network(s=matrices, frequency=skrfFrequency, z0=z0)
    net.write_touchstone("raw_meas_for_simple_compensation.s2p")


print("Take calibration data")
if SUPPORTS_S11:
    print("Taking data for calibration S11: \n")
    take_short_S11()
    take_open_S11()
    take_load_S11()
if SUPPORTS_S22:
    print("Taking data for calibration S22: \n")
    take_short_S22()
    take_open_S22()
    take_load_S22()

take_transmission_open()
take_transmission_thru()

# print("Calibration Data is taken")

print("Take DUT measurements: (raw uncalibrated)")
take_raw_measurements()

driver.close()
