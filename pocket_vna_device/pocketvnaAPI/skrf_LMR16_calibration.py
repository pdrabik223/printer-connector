import skrf
import numpy
import numpy as np

import pylab


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


raw = skrf.Network("calibration_data_lmr16/meas.s2p")


freq = raw.f

ntwk_thru = build_ideal(freq, 0.0, 1.0, 1.0, 0.0, 50.0)
ntwk_refl_shrt = build_ideal(freq, -1.0, 0.0, 0.0, -1.0, 50.0)
ntwk_refl_opn = build_ideal(freq, 1.0, 0.0, 0.0, 1.0, 50.0)
# =========================

thr = skrf.Network("calibration_data_lmr16/lmr16-through.s2p")
m_m = skrf.Network("calibration_data_lmr16/lmr16-match-match.s2p")
r_r = skrf.Network("calibration_data_lmr16/lmr16-reflect-reflect.s2p")
r_m = skrf.Network("calibration_data_lmr16/lmr16-reflect-match.s2p")
m_r = skrf.Network("calibration_data_lmr16/lmr16-match-reflect.s2p")

complex_formatter = lambda x: "({0.real:.7f} + {0.imag:.7f}i)".format(x)
np.set_printoptions(formatter={"complex_kind": complex_formatter})


float_formatter = lambda x: "%.7f" % x
np.set_printoptions(formatter={"float_kind": float_formatter})


# def stata(arr):
#     return np.mean( np.abs(arr) )

# def convt(net):
#     return np.array([ [ stata( net.z[:,0,0] ), stata( net.z[:,0,1] ) ],
#                       [ stata( net.z[:,1,0] ), stata( net.z[:,1,1] ) ] ])

# mean_th = convt(thr)

# mean_mm = convt(m_m)

# mean_rr = convt(r_r)

# mean_rm = convt(r_m)

# mean_mr = convt(m_r)

# print("\tTHROUGH")
# print(mean_th)

# print("\n\tMATCH-MATCH")
# print(mean_mm)

# print("\n\tREFLECT-REFLECT")
# print(mean_rr)

# print("\n\tREFLECT-MATCH")
# print(mean_rm)

# print("\n\MATCH-REFLECT")
# print(mean_mr)

# ____________________________________________________________


# cal_refl_open = skrf.LMR16(\
#         measured = [thr, m_m, r_r, r_m, m_r],
#         ideals = ntwk_refl_opn,
#         ideal_is_reflect = True
#         )
cal_refl_short = skrf.LMR16(
    measured=[thr, m_m, r_r, r_m, m_r], ideals=ntwk_refl_shrt, ideal_is_reflect=True
)
cal_thru = skrf.LMR16(
    measured=[thr, m_m, r_r, r_m, m_r], ideals=ntwk_thru, ideal_is_reflect=False
)

print("\n\tCALIBRATION IS MADE: ")

# dut_op = cal_refl_open.apply_cal(raw)
# dut_op.write_touchstone(filename='calibration_data_lmr16/_dut_by_open_refl.s2p')
# print("\tDUT calibrated against OPEN-REFLECT is saved")

dut_sh = cal_refl_short.apply_cal(raw)
dut_sh.write_touchstone(filename="calibration_data_lmr16/_dut_by_short_refl.s2p")
print("\tDUT calibrated against SHORT-REFLECT is saved")


dut_thr = cal_thru.apply_cal(raw)
dut_thr.write_touchstone(filename="calibration_data_lmr16/_dut_by_thru.s2p")
print("\tDUT calibrated against THROUGH is saved\n\t\tThe END!")


def plotX(fig, vct):
    pylab.figure(fig)
    pylab.title("WR-10 Ringslot Array, Mag-00")
    vct.plot_s_db(m=0, n=0)  # m,n are S-Matrix indices
    pylab.figure(fig + 1)
    pylab.title("WR-10 Ringslot Array, Mag-11")
    vct.plot_s_db(m=1, n=1)  # m,n are S-Matrix indices
    # show the plots


# plotX(1, dut_op)
plotX(1, dut_sh)
# plotX(3, dut_thr)

pylab.show()
