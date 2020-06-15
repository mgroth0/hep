from __init__ import *
from qrsalg import *
SUBJECTS = [
    HEP_Subject(
        'EP1163',
        [
            # 'TEN_SECOND_PILOT'
            # 'TEN_MINUTE_TEST'
            'FULL'
        ][0], [
            # (ManualPeakDetection, inf, 'LOAD'),
            (ecglab_fast, inf, 'CALC'),
            # (ecglab_fast, inf, 'CALC'),
            # (ecglab_slow, inf, 'CALC'),
            # JustPreprocess
            # (pan_tompkins, inf, 'CALC'),

        ][x]
    ) for x in range(1)]
SAVE = True
# RAND_SLICE = slice(559 * SUBJECTS[0].get_Fs(), 559.25 * SUBJECTS[0].get_Fs())
RAND_SLICE = slice(555 * SUBJECTS[0].get_Fs(), 562 * SUBJECTS[0].get_Fs())
# RAND_SLICE = slice(0 * SUBJECTS[0].get_Fs(), 590 * SUBJECTS[0].get_Fs())
PLOT = ''.join([
    'IMAGE',
    # 'GUI'
])
