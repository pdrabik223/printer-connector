import skrf
import numpy


def build_freq():
    start, end, steps = 1000000, 100000000, 100

    return numpy.linspace(start, end, steps, dtype=numpy.uint64)


def build_ideal(freq, s11, s21, s12, s22, z0):
    s = numpy.zeros((len(freq), 2, 2), dtype=numpy.complex128)

    for i in range(0, len(freq)):
        s[i, 0, 0], s[i, 0, 1] = s11, s12
        s[i, 1, 0], s[i, 1, 1] = s21, s22

    ntwk = skrf.Network()
    ntwk.s = s
    ntwk.frequency = skrf.Frequency.from_f(freq, unit="hz")
    ntwk.z0 = z0

    return ntwk


freq = build_freq()
ntwk_thru = build_ideal(freq, 0.0, 1.0, 1.0, 0.0, 50.0)
ntwk_short_short = build_ideal(freq, -1.0, 0.0, 0.0, -1.0, 50.0)
ntwk_open_open = build_ideal(freq, 1.0, 0.0, 0.0, 1.0, 50.0)
ntwk_load_load = build_ideal(freq, 0.0, 0.0, 0.0, 0.0, 50.0)
# =========================
my_ideals = [ntwk_short_short, ntwk_open_open, ntwk_load_load, ntwk_thru]

my_measured = [
    skrf.Network("short_short.s2p"),
    skrf.Network("open_open.s2p"),
    skrf.Network("load_load.s2p"),
    skrf.Network("through.s2p"),
]

##

# ideals = [
#     wg.short(nports=2, name='short'),
#     wg.open(nports=2, name='open'),
#     wg.match(nports=2, name='load'),
#     None,
#     ]
# actuals = [
#     wg.short(nports=2, name='short'),
#     wg.open(nports=2, name='open'),
#     wg.match(nports=2, name='load'),
#     wg.thru(),
#     ]


##


cal = skrf.SOLT(
    ideals=my_ideals,
    measured=my_measured,
)

print("CALIBRATION IS MADE: ")
dut = skrf.Network("meas.s2p")

dut_cal = cal.apply_cal(dut)

dut_cal.write_touchstone(filename="_dutsolt.s2p")

print("CALIBRATOIN IS PERFORMED")
