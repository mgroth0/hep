from HEP_lib import HEP_Subject
from numpy import inf
from qrsalg import *
from qrsalg import ManualPeakDetection
SUBJECTS = [
    HEP_Subject(
        'EP1163',
        [
            'TEN_SECOND_PILOT'
            # 'TEN_MINUTE_TEST'
            # 'FULL'
        ][0], [
            (ManualPeakDetection, inf, 'CALC'),
            (ECGLAB_Original, inf, 'CALC'),
            # (ecglab_fast, inf, 'CALC'),
            # (ecglab_slow, inf, 'CALC'),
            # (pan_tompkins, inf, 'CALC'),

        ][x]
    ) for x in range(2)]
SAVE = False

RAND_SLICE = slice(2 * SUBJECTS[0].get_Fs(), 8 * SUBJECTS[0].get_Fs())

# this was used for full
# RAND_SLICE = slice(555 * SUBJECTS[0].get_Fs(), 562 * SUBJECTS[0].get_Fs())

PLOT_FILE = '_plot.png'
# PLOT_FILE = None #GUI
