"""@package pocketvna_calibration_loader
Python loader of *.cali calibration file
# @file
#  @defgroup API pocketVna API
"""
import os
import re

from types import *


NUMPY = None
try:
    import numpy

    NUMPY = True
except ImportError:
    NUMPY = False

SKRF = None
try:
    import skrf

    SKRF = True
except ImportError:
    SKRF = False

SCIPY = None
try:
    import scipy

    SCIPY = True
except ImportError:
    SCIPY = False


class CalibrationAlgo:
    SIMPLE_SOLT = "simple-solt"
    TOSM = "TOSM"
    LMR16 = "LMR16"
    TRL8 = "TRL"
    UNKNOWN = "unknown"


def to_frequency_number(str):
    return int(str)


def is_empty(array):
    return len(array) < 1


def build_ideal(freq, s11, s21, s12, s22, z0):
    if not SKRF:
        raise Exception("No  scikit-rf  library imported")
    if not NUMPY:
        raise Exception("No  numpy  library imported")

    s = numpy.zeros((len(freq), 2, 2), dtype=numpy.complex128)

    for i in range(0, len(freq)):
        s[i, 0, 0], s[i, 0, 1] = s11, s12
        s[i, 1, 0], s[i, 1, 1] = s21, s22

    ntwk = skrf.Network()
    ntwk.s = s
    ntwk.frequency = skrf.Frequency.from_f(freq, unit="hz")
    ntwk.z0 = z0

    return ntwk


def ensure_length(size, array):
    assert is_empty(array) or len(array) == size
    if len(array) == size:
        return array
    else:
        return numpy.zeros(size, dtype=numpy.complex128)


def gen_zeros(size):
    return ensure_length(size, [])


def build_network(freq, s11, s21, s12, s22, z0):
    if not SKRF:
        raise Exception("No  scikit-rf  library imported")
    if not NUMPY:
        raise Exception("No  numpy  library imported")

    assert (
        len(freq) == len(s11)
        and len(freq) == len(s21)
        and len(freq) == len(s12)
        and len(freq) == len(s22)
    )

    s = numpy.zeros((len(freq), 2, 2), dtype=numpy.complex128)

    s[:, 0, 0], s[:, 0, 1] = s11, s12
    s[:, 1, 0], s[:, 1, 1] = s21, s22

    ntwk = skrf.Network()
    ntwk.s = s
    ntwk.frequency = skrf.Frequency.from_f(freq, unit="hz")
    ntwk.z0 = z0

    return ntwk

    return ntwk


def interpolate_array(x, y, newX):
    assert len(x) == len(y)

    interp_re = scipy.interpolate.interp1d(x, y.real)
    interp_im = scipy.interpolate.interp1d(x, y.imag)

    return interp_re(newX) + 1j * interp_im(newX)


class ScanRange:
    def __init__(self, start, end, steps):
        self.vstart = float(start)
        self.vend = float(end)
        self.vsteps = int(steps)

    def start(self):
        return self.vstart

    def end(self):
        return self.vend

    def steps(self):
        return self.vsteps

    def __str__(self):
        return (
            "[ "
            + str(self.start())
            + " Hz; "
            + str(self.end())
            + " ] / "
            + str(self.steps())
        )


class CalibrationData:
    def __init__(self, forCopy=None):
        if forCopy is None:
            self.count = 0
            self.info = None
            self.reference_resistance = 0.0
            self.algo = None
            self.scanrange = None
            self.data = {}
        else:
            self.count = forCopy.size()
            self.info = forCopy.__getattribute__("info")
            self.reference_resistance = forCopy.__getattribute__("reference_resistance")
            self.algo = forCopy.__getattribute__("algo")
            self.scanrange = forCopy.__getattribute__("scanrange")
            self.data = {}

    def isReady():
        return None

    def isEmpty(self):
        return is_empty(self.frequency())

    def setReferenceResistance(self, z0):
        self.reference_resistance = z0

    def setSize(self, size):
        self.count = size

    def setScanRange(self, scanrange):
        assert isinstance(scanrange, ScanRange), "should be ScanRange instance"
        self.scanrange = scanrange

    def setInfo(self, soft_firm_info):
        self.info = soft_firm_info

    def setAlgorithm(self, algo):
        self.algo = algo

    def algorithm(self):
        return self.algo

    def scanRange(self):
        return self.scanrange

    def referenceResistance(self):
        return self.reference_resistance

    def size(self):
        return self.count

    def dataMap(self):
        return self.data

    def frequency(self):
        return self.parameter(CalibrationFileLoader.FREQ_COLUMN)

    def parameter(self, columnTitle):
        return self.data[columnTitle] if columnTitle in self.data else []

    def addColumn(self, columntitle):
        self.data[columntitle] = []

    def appendIntoColumn(self, columntitle, cellvalue):
        self.data[columntitle].append(cellvalue)


class SimpleCalibrationData(CalibrationData):
    SHORT_S11_TITLE = "shortz11"
    OPEN_S11_TITLE = "openz11"
    LOAD_S11_TITLE = "loadz11"

    SHORT_S22_TITLE = "shortz22"
    OPEN_S22_TITLE = "openz22"
    LOAD_S22_TITLE = "loadz22"

    OPEN_S21_TITLE = "opens21"
    THRU_S21_TITLE = "throughs21"

    OPEN_S12_TITLE = "opens12"
    THRU_S12_TITLE = "throughs12"

    def __init__(self, forCopy=None):
        CalibrationData.__init__(self, forCopy)

    def isFull(self):
        return (
            self.isS11Ready()
            and self.isS22Ready()
            and self.isS21Ready()
            and self.isS12Ready()
        )

    # -----------  S11  ---------------
    def shortS11(self):
        return self.parameter(SimpleCalibrationData.SHORT_S11_TITLE)

    def openS11(self):
        return self.parameter(SimpleCalibrationData.OPEN_S11_TITLE)

    def loadS11(self):
        return self.parameter(SimpleCalibrationData.LOAD_S11_TITLE)

    def isS11Ready(self):
        return (
            not self.isEmpty()
            and len(self.frequency()) == len(self.shortS11())
            and len(self.frequency()) == len(self.openS11())
            and len(self.frequency()) == len(self.loadS11())
        )

    # -----------  S21  ---------------
    def openS21(self):
        return self.parameter(SimpleCalibrationData.OPEN_S21_TITLE)

    def thruS21(self):
        return self.parameter(SimpleCalibrationData.THRU_S21_TITLE)

    def isS21Ready(self):
        return (
            not self.isEmpty()
            and len(self.frequency()) == len(self.openS21())
            and len(self.frequency()) == len(self.thruS21())
        )

    # -----------  S12 ---------------
    def openS12(self):
        return self.parameter(SimpleCalibrationData.OPEN_S12_TITLE)

    def thruS12(self):
        return self.parameter(SimpleCalibrationData.THRU_S12_TITLE)

    def isS12Ready(self):
        return (
            not self.isEmpty()
            and len(self.frequency()) == len(self.openS12())
            and len(self.frequency()) == len(self.thruS12())
        )

    # ------- S22 ------------------
    def shortS22(self):
        return self.parameter(SimpleCalibrationData.SHORT_S22_TITLE)

    def openS22(self):
        return self.parameter(SimpleCalibrationData.OPEN_S22_TITLE)

    def loadS22(self):
        return self.parameter(SimpleCalibrationData.LOAD_S22_TITLE)

    def isS22Ready(self):
        return (
            not self.isEmpty()
            and len(self.frequency()) == len(self.shortS22())
            and len(self.frequency()) == len(self.openS22())
            and len(self.frequency()) == len(self.loadS22())
        )

    def isReady(self):
        return (
            self.isS11Ready()
            or self.isS22Ready()
            or self.isS21Ready()
            and self.isS12Ready()
        )

    def interpolate(self, newFrequencies):
        newf = numpy.array(newFrequencies, dtype=numpy.float64)
        new_data = SimpleCalibrationData(forCopy=self)
        assert new_data.algorithm() == self.algorithm()

        columntitles = [
            SimpleCalibrationData.SHORT_S11_TITLE,
            SimpleCalibrationData.OPEN_S11_TITLE,
            SimpleCalibrationData.LOAD_S11_TITLE,
            SimpleCalibrationData.SHORT_S22_TITLE,
            SimpleCalibrationData.OPEN_S22_TITLE,
            SimpleCalibrationData.LOAD_S22_TITLE,
            SimpleCalibrationData.OPEN_S21_TITLE,
            SimpleCalibrationData.THRU_S21_TITLE,
            SimpleCalibrationData.OPEN_S12_TITLE,
            SimpleCalibrationData.THRU_S12_TITLE,
        ]
        # Register columns
        new_data.addColumn(CalibrationFileLoader.FREQ_COLUMN)
        for title in columntitles:
            new_data.addColumn(title)

        # Interpolate and insert
        new_data.dataMap()[CalibrationFileLoader.FREQ_COLUMN] = newf
        for title in columntitles:
            array = self.parameter(title)
            if array is not None:
                if not is_empty(array):
                    new_data.dataMap()[title] = interpolate_array(
                        self.frequency(),
                        numpy.array(array, dtype=numpy.complex128),
                        newf,
                    )

        return new_data


# True SOLT / TOSM
class TOSMCalibrationData(CalibrationData):
    SHRT_S11_TITLE = "shorts11"
    OPEN_S11_TITLE = "opens11"
    LOAD_S11_TITLE = "loads11"

    SHRT_S22_TITLE = "shorts22"
    OPEN_S22_TITLE = "opens22"
    LOAD_S22_TITLE = "loads22"

    LOAD_S21_TITLE = "loads21"
    THRU_S11_TITLE = "throughs11"
    THRU_S21_TITLE = "throughs21"

    LOAD_S12_TITLE = "loads12"
    THRU_S22_TITLE = "throughs22"
    THRU_S12_TITLE = "throughs12"

    def __init__(self):
        CalibrationData.__init__(self)

    def isReady(self):
        return (
            not self.isEmpty()
            and len(self.shortS11()) == len(self.frequency())
            and len(self.openS11()) == len(self.frequency())
            and len(self.matchS11()) == len(self.frequency())
            and len(self.thruS11()) == len(self.frequency())
            and len(self.thruS21()) == len(self.frequency())
            and len(self.shortS22()) == len(self.frequency())
            and len(self.openS22()) == len(self.frequency())
            and len(self.matchS22()) == len(self.frequency())
            and len(self.thruS22()) == len(self.frequency())
            and len(self.thruS12()) == len(self.frequency())
            and (
                is_empty(self.matchS21())
                or len(self.matchS21()) == len(self.frequency())
            )
            and (
                is_empty(self.matchS12())
                or len(self.matchS12()) == len(self.frequency())
            )
        )

    # -
    def shortS11(self):
        return self.parameter(TOSMCalibrationData.SHRT_S11_TITLE)

    def openS11(self):
        return self.parameter(TOSMCalibrationData.OPEN_S11_TITLE)

    def matchS11(self):
        return self.parameter(TOSMCalibrationData.LOAD_S11_TITLE)

    # - -
    def matchS21(self):
        return self.parameter(TOSMCalibrationData.LOAD_S21_TITLE)

    def thruS11(self):
        return self.parameter(TOSMCalibrationData.THRU_S11_TITLE)

    def thruS21(self):
        return self.parameter(TOSMCalibrationData.THRU_S21_TITLE)

    # -
    def shortS22(self):
        return self.parameter(TOSMCalibrationData.SHRT_S22_TITLE)

    def openS22(self):
        return self.parameter(TOSMCalibrationData.OPEN_S22_TITLE)

    def matchS22(self):
        return self.parameter(TOSMCalibrationData.LOAD_S22_TITLE)

    # - -
    def matchS12(self):
        return self.parameter(TOSMCalibrationData.LOAD_S12_TITLE)

    def thruS22(self):
        return self.parameter(TOSMCalibrationData.THRU_S22_TITLE)

    def thruS12(self):
        return self.parameter(TOSMCalibrationData.THRU_S12_TITLE)

    def isNeglectIsolation(self):
        return is_empty(self.matchS21()) or is_empty(self.matchS12())

    def gen_ideal_networks(self, new_frequencies=None):
        """
        Requires numpy and scikit-rf installed
        Generate required networks with IDEALS to use SKRF's calibration classes
        """
        freq = self.frequency() if new_frequencies is None else new_frequencies
        z0 = self.referenceResistance()
        ntwk_thru = build_ideal(freq, 0.0, 1.0, 1.0, 0.0, z0)
        ntwk_short_short = build_ideal(freq, -1.0, 0.0, 0.0, -1.0, z0)
        ntwk_open_open = build_ideal(freq, 1.0, 0.0, 0.0, 1.0, z0)
        ntwk_load_load = build_ideal(freq, 0.0, 0.0, 0.0, 0.0, z0)

        return [ntwk_short_short, ntwk_open_open, ntwk_load_load, ntwk_thru]

    def gen_short_short_network(self):
        freq = self.frequency()
        size = len(freq)
        z0 = self.referenceResistance()
        return build_network(
            freq, self.shortS11(), gen_zeros(size), gen_zeros(size), self.shortS22(), z0
        )

    def gen_open_open_network(self):
        freq = self.frequency()
        size = len(freq)
        z0 = self.referenceResistance()
        return build_network(
            freq, self.openS11(), gen_zeros(size), gen_zeros(size), self.openS22(), z0
        )

    def gen_match_match_network(self):
        freq = self.frequency()
        size = len(freq)
        z0 = self.referenceResistance()
        return build_network(
            freq,
            ensure_length(size, self.matchS11()),
            ensure_length(size, self.matchS21()),
            ensure_length(size, self.matchS12()),
            ensure_length(size, self.matchS11()),
            z0,
        )

    def gen_thru_network(self):
        freq = self.frequency()
        size = len(freq)
        z0 = self.referenceResistance()
        return build_network(
            freq, self.thruS11(), self.thruS21(), self.thruS12(), self.thruS22(), z0
        )

    def gen_standard_networks(self):
        """
        Requires numpy and scikit-rf installed
        Generate required networks with STANDARDS to use SKRF's calibration classes
        """
        freq = self.frequency()
        return [
            self.gen_short_short_network(),
            self.gen_open_open_network(),
            self.gen_match_match_network(),
            self.gen_thru_network(),
        ]


class CalibrationFileLoader:
    CALIBRATION_FILE_TAG = "#pvna1"
    CALIBRATION_LMR16 = "#lmr16/16-term"
    CALIBRATION_SIMPLE = "#simple-2port"
    CALIBRATION_TOSM = "#solt/tosm"
    CALIBRATION_TRL = "#tlr/8-term"

    CALIBRATION_OPTION_TAG = "!"
    CALIBRATOIN_DATA_START_TAG = "{startcali:"
    CALIBRATION_DATA_END_TAG = "}endcali"

    CALIBRATION_OPTION_DISTR = "distr"
    CALIBRATION_REF_R = "rr"

    RANGE_TAG = CALIBRATION_OPTION_TAG + "range" + ":"
    DISTR_TAG = CALIBRATION_OPTION_TAG + CALIBRATION_OPTION_DISTR + ":"
    RR_TAG = CALIBRATION_OPTION_TAG + CALIBRATION_REF_R + ":"
    IGNORABLE_Z0_TAG = CALIBRATION_OPTION_TAG + "z0" + ":"
    DATE_TAG = CALIBRATION_OPTION_TAG + "date" + ":"
    SIZE_TAG = CALIBRATION_OPTION_TAG + "size" + ":"
    INFO_TAG = CALIBRATION_OPTION_TAG + "soft" + ":"
    FREQ_COLUMN = "frq"

    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.calidata = None
        self.current_line_number = 0

    def parse(self):
        try:
            if not self._open_file():
                return None

            calitype = self._read_cali_type()
            if calitype == CalibrationAlgo.SIMPLE_SOLT:
                self.calidata = SimpleCalibrationData()
            elif calitype == CalibrationAlgo().TOSM:
                self.calidata = TOSMCalibrationData()
            else:
                self.calidata = CalibrationData()

            self.calidata.setAlgorithm(calitype)

            if self.calidata.algorithm() is None:
                return None
            else:
                self._read_settings()
                return self.calidata

        finally:
            self._close_file()

    def _open_file(self):
        try:
            self.file = open(self.filename, "r")
            return True
        except IOError:
            return False

    def _close_file(self):
        if self.file != None:
            self.file.close()

    def _read_cali_type(self):
        headLine = self._read_line()
        if headLine is None:
            return None

        if headLine.startswith(CalibrationFileLoader.CALIBRATION_FILE_TAG):
            if headLine.startswith(
                CalibrationFileLoader.CALIBRATION_FILE_TAG
                + "#"
                + CalibrationFileLoader.CALIBRATION_LMR16
            ):
                return CalibrationAlgo.LMR16
            elif headLine.startswith(
                CalibrationFileLoader.CALIBRATION_FILE_TAG
                + "#"
                + CalibrationFileLoader.CALIBRATION_SIMPLE
            ):
                return CalibrationAlgo.SIMPLE_SOLT
            elif headLine.startswith(
                CalibrationFileLoader.CALIBRATION_FILE_TAG
                + "#"
                + CalibrationFileLoader.CALIBRATION_TOSM
            ):
                return CalibrationAlgo.TOSM
            elif headLine.startswith(
                CalibrationFileLoader.CALIBRATION_FILE_TAG
                + "#"
                + CalibrationFileLoader.CALIBRATION_TRL
            ):
                return CalibrationAlgo.TRL8
            elif headLine == CalibrationFileLoader.CALIBRATION_FILE_TAG:
                return CalibrationAlgo.SIMPLE_SOLT

            return CalibrationAlgo.UNKNOWN
        else:
            return None

    def _read_line(self):
        line = self.file.readline()
        if not line:
            return None

        self.current_line_number += 1

        return line.lower().strip()

    def _read_settings(self):
        data_found = False

        while True:
            line = self._read_line()

            if not line:
                break

            if line.startswith(CalibrationFileLoader.CALIBRATOIN_DATA_START_TAG):
                data_found = True
                break

            elif line.startswith(CalibrationFileLoader.CALIBRATION_OPTION_TAG):
                self._process_option(line)

            elif not line:
                # line is empty
                print("empty line")

            else:
                print("Unexpected Line: " + line)

        if data_found:
            self._parse_data_section()

        else:
            print(" No Data Settings")

    def _parse_data_section(self):
        titlesline = self._read_line()

        self._collect_columns(titlesline.split(";"))

        if (
            len(self.calidata.dataMap()) == len(self.column_indeces)
            and len(self.column_indeces) > 0
        ):
            self._parse_rows()

    def _collect_columns(self, titles):
        assert type(titles) is list, "`titles` is not a List. " + str(type(titles))

        self.column_indeces = {}

        column_index = 0
        for f in titles:
            self._register_column(f.strip(), column_index)
            column_index += 1

    def _register_column(self, key, columnindex):
        if key:
            self.calidata.addColumn(key)
            self.column_indeces[columnindex] = key

    def _parse_rows(self):
        while True:
            line = self._read_line()

            assert not not line, "Unexpected End Of File#" + str(
                self.current_line_number
            )

            if line.startswith(CalibrationFileLoader.CALIBRATION_DATA_END_TAG):
                break

            self._collect_cells(line.split(";"))

    def _collect_cells(self, cells):
        assert type(cells) is list, "`cells` is not a List"

        column_index = 0

        for i in cells:
            cell = i.strip()
            if not cell:
                continue

            self._parse_cell(column_index, cell)

            column_index += 1

    def isFrequency(self, columntitle):
        return columntitle == CalibrationFileLoader.FREQ_COLUMN

    def _parse_cell(self, columnindex, cellstr):
        key = self.column_indeces[columnindex]

        if self.isFrequency(key):
            self.calidata.appendIntoColumn(key, to_frequency_number(cellstr))
        else:
            complexes = cellstr.split(",")
            assert len(complexes) == 2, (
                "Complex number should contain 2 elements line#"
                + str(self.current_line_number)
                + " at "
                + str(columnindex + 1)
            )

            self.calidata.appendIntoColumn(
                key, complex(float(complexes[0]), float(complexes[1]))
            )

    def _process_option(self, line):
        if line.startswith(CalibrationFileLoader.RANGE_TAG):
            range_re = "^\\!range\\:\\s*\\[\\s*(\\d+)\\s*;\\s*(\\d+)\\s*\\]\\s*\\/\\s*(\\d+)\\s*$"
            m = re.search(range_re, line)
            f_from = m.group(1)
            f_to = m.group(2)
            f_steps = m.group(3)

            self.calidata.setScanRange(ScanRange(f_from, f_to, f_steps))

        elif line.startswith(CalibrationFileLoader.DISTR_TAG):
            print(
                "Distribution => "
                + line.replace(CalibrationFileLoader.DISTR_TAG, "").strip()
            )

        elif line.startswith(CalibrationFileLoader.RR_TAG):
            self.calidata.setReferenceResistance(
                float(line.replace(CalibrationFileLoader.RR_TAG, "").strip())
            )

        elif line.startswith(CalibrationFileLoader.IGNORABLE_Z0_TAG):
            print(
                "Ignore Z0 => "
                + line.replace(CalibrationFileLoader.IGNORABLE_Z0_TAG, "").strip()
            )

        elif line.startswith(CalibrationFileLoader.DATE_TAG):
            print("Date => " + line.replace(CalibrationFileLoader.DATE_TAG, "").strip())

        elif line.startswith(CalibrationFileLoader.SIZE_TAG):
            self.calidata.setSize(
                int(line.replace(CalibrationFileLoader.SIZE_TAG, "").strip())
            )

        elif line.startswith(CalibrationFileLoader.INFO_TAG):
            self.calidata.setInfo(
                line.replace(CalibrationFileLoader.INFO_TAG, "").strip()
            )

        else:
            print("Unexpected tag => " + line)
