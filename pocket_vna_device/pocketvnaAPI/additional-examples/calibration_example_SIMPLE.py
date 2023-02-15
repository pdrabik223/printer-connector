import pocketvna_calibration_loader as caliloader

import math
import cmath
import os

MATPLOT = None
try:
    import matplotlib.pyplot as plot

    MATPLOT = True
except ImportError:
    MATPLOT = False

import skrf
import numpy

dir_path = os.path.dirname(os.path.realpath(__file__))

CALIBRATION_FILE = dir_path + "/FULL_SOLT_1KIT.cali"
RAW_DATA_FILE = dir_path + "/some_raw_data.s2p"

# Loading calibration file

loader = caliloader.CalibrationFileLoader(CALIBRATION_FILE)
caliData = loader.parse()

if caliData is None:
    print("Could not load file " + CALIBRATION_FILE)
    exit(1)

if caliData.algorithm() != caliloader.CalibrationAlgo.SIMPLE_SOLT:
    print("This example works for simple calibration ONLY ")
    exit(2)

dut = skrf.Network(RAW_DATA_FILE)

#
# Pay attention: GUI app uses a bit different way for interpolation
#
interpolatedCalibrationData = caliData.interpolate(dut.f)


# ---------  FORMULAS ------------------------------------------
def gamma_2_z(snn, z0):
    return skrf.tlineFunctions.Gamma0_2_zl(z0, snn)


def z_2_gamma(znn, z0):
    return skrf.tlineFunctions.zl_2_Gamma0(z0, znn)


## formula for compensation for S11/S22 (reflection)
def reflection_compensation_formula(Zstd, Zo, Zsm, Zs, Zxm):
    return (Zstd * (Zo - Zsm) * (Zxm - Zs)) / ((Zsm - Zs) * (Zo - Zxm))


## formula for compensation for S21/S12 (transmission)
def transmission_compensation_formula(Sxm, So, Sthru):
    return (Sxm - So) / (Sthru - So)


# applying formula using calibration data + raw data
def reflection_compensation(Z0, RawSnn, ShortSnn, OpenSnn, LoadSnn):
    zstd = Z0
    zo = gamma_2_z(OpenSnn, Z0)
    zsm = gamma_2_z(LoadSnn, Z0)
    zs = gamma_2_z(ShortSnn, Z0)
    zxm = gamma_2_z(RawSnn, Z0)

    zdut = reflection_compensation_formula(zstd, zo, zsm, zs, zxm)

    return z_2_gamma(zdut, Z0)


# applying formula using calibration data + raw data
def transmission_compensation(RawSnm, OpenSnm, ThruSnm):
    return transmission_compensation_formula(RawSnm, OpenSnm, ThruSnm)


# ------------- Compensation Application --------------------------
calibratedS = numpy.zeros((len(dut.f), 2, 2), dtype=numpy.complex128)

if interpolatedCalibrationData.isS11Ready():
    calibratedS[:, 0, 0] = reflection_compensation(
        interpolatedCalibrationData.referenceResistance(),
        dut.s[:, 0, 0],
        interpolatedCalibrationData.shortS11(),
        interpolatedCalibrationData.openS11(),
        interpolatedCalibrationData.loadS11(),
    )

if interpolatedCalibrationData.isS21Ready():
    calibratedS[:, 1, 0] = transmission_compensation(
        dut.s[:, 1, 0],
        interpolatedCalibrationData.openS21(),
        interpolatedCalibrationData.thruS21(),
    )

if interpolatedCalibrationData.isS12Ready():
    calibratedS[:, 0, 1] = transmission_compensation(
        dut.s[:, 0, 1],
        interpolatedCalibrationData.openS12(),
        interpolatedCalibrationData.thruS12(),
    )

if interpolatedCalibrationData.isS22Ready():
    calibratedS[:, 1, 1] = reflection_compensation(
        interpolatedCalibrationData.referenceResistance(),
        dut.s[:, 1, 1],
        interpolatedCalibrationData.shortS22(),
        interpolatedCalibrationData.openS22(),
        interpolatedCalibrationData.loadS22(),
    )

dut_calibrated = skrf.Network(
    f=dut.f, s=calibratedS, z0=interpolatedCalibrationData.referenceResistance()
)

# ------------- PLOT -----------------
if MATPLOT:
    plot.figure(1)
    dut_calibrated.plot_s_db(m=0, n=0, label="S11")
    dut_calibrated.plot_s_db(m=1, n=1, label="S22")

    plot.figure(2)
    dut_calibrated.plot_s_smith(m=0, n=0, draw_labels=True)
    dut_calibrated.plot_s_smith(m=1, n=1, draw_labels=True)

    plot.show()
