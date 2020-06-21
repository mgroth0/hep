from HEP_lib import HEP_Subject
from numpy import inf

from mlib.boot.mutil import Folder
from mlib.web.makereport_lib import DOCS_FOLDER
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

RAND_SLICE = slice(2 * SUBJECTS[0].Fs, 8 * SUBJECTS[0].Fs)

# this was used for full
# RAND_SLICE = slice(555 * SUBJECTS[0].get_Fs(), 562 * SUBJECTS[0].get_Fs())

_FIGS_FOLDER = Folder(DOCS_FOLDER.mkdir()['resources/figs']).mkdirs()
PLOT_FILE = _FIGS_FOLDER['plot.png']
# PLOT_FILE = None #GUI
