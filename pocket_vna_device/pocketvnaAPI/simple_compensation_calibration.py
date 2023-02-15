"""
Example of performing calibration
this file is linked tightly to make_simple_compensation_standatrd.py
"""
import skrf
import numpy


def load_file_or_return_nil(filename):
    try:
        return skrf.Network(filename)
    except IOError:
        return None


shortS11 = load_file_or_return_nil("simple_compensation_s11_short.s1p")
openS11 = load_file_or_return_nil("simple_compensation_s11_open.s1p")
loadS11 = load_file_or_return_nil("simple_compensation_s11_load.s1p")


shortS22 = load_file_or_return_nil("simple_compensation_s22_short.s1p")
openS22 = load_file_or_return_nil("simple_compensation_s22_open.s1p")
loadS22 = load_file_or_return_nil("simple_compensation_s22_load.s1p")


thruTrans = load_file_or_return_nil("simple_compensation_thru_trans.s2p")
openTrans = load_file_or_return_nil("simple_compensation_open_trans.s2p")


rawMeas = load_file_or_return_nil("raw_meas_for_simple_compensation.s2p")

assert not (rawMeas is None), "No raw measurements are provided"

# check that calibration data for S11 is provided
readyFor11 = not ((shortS11 is None) or (openS11 is None) or (loadS11 is None))
# check that calibration data for S22 is provided
readyFor22 = not ((shortS22 is None) or (openS22 is None) or (loadS22 is None))
# S21 is linked to S11, so ready for S21 should be ready for S11 too
readyFor21 = not ((thruTrans is None) or (openTrans is None)) and readyFor11
# S12 is linked to S22, so ready for S12 should be ready for S22 too
readyFor12 = readyFor21 and readyFor22


# for a 2 port network, z0 is array (of len(rawMeas)), not single number
# and each row has 2 numbers: one per port
# fot our purpose they should be equal
z0 = rawMeas.z0[:, 0]


# Check length of all parameters are equal
if readyFor11:
    assert (
        len(shortS11) == len(rawMeas)
        and len(openS11) == len(rawMeas)
        and len(loadS11) == len(rawMeas)
    )

if readyFor22:
    assert (
        len(shortS22) == len(rawMeas)
        and len(openS22) == len(rawMeas)
        and len(loadS22) == len(rawMeas)
    )

if readyFor21 or readyFor12:
    assert len(thruTrans) == len(rawMeas) and len(openTrans) == len(rawMeas)

HAS_S11 = readyFor11
HAS_S21 = readyFor21
HAS_S12 = readyFor12
HAS_S22 = readyFor22


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


dut = numpy.zeros((len(rawMeas), 2, 2), dtype=numpy.complex128)


if HAS_S11:
    dut[:, 0, 0] = reflection_compensation(
        z0, rawMeas.s[:, 0, 0], shortS11.s[:, 0], openS11.s[:, 0], loadS11.s[:, 0]
    )

if HAS_S21:
    dut[:, 1, 0] = transmission_compensation(
        rawMeas.s[:, 1, 0], openTrans.s[:, 1, 0], thruTrans.s[:, 1, 0]
    )

if HAS_S12:
    dut[:, 0, 1] = transmission_compensation(
        rawMeas.s[:, 0, 1], openTrans.s[:, 0, 1], thruTrans.s[:, 1, 0]
    )

if HAS_S22:
    dut[:, 1, 1] = reflection_compensation(
        z0,
        rawMeas.s[:, 1, 1],
        shortS22.s[:, 0, 0],
        openS22.s[:, 0, 0],
        loadS22.s[:, 0, 0],
    )


print("CALIBRATION IS MADE")
dut = skrf.Network(s=dut, frequency=rawMeas.frequency, z0=rawMeas.z0)
dut.write_touchstone(filename="_dut.s2p")

print("Calibrated data is stored")
