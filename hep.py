import random

from math import inf
import numpy as np

from mlib.proj.struct import Project


_SAVE_DATA = False
COMPARE_IBI = False

class HEP(Project):
    def run(self, cfg):
        self.daily_reminder('remember to update algorithm versions')
        from HEP_lib import compare_IBI, HEP_Subject
        from mlib.boot import log
        from mlib.web.shadow import Shadow
        from qrsalg import ECGLAB_Original
        from mlib import term
        term.Progress.PROGRESS_DISABLED = False
        shadow = Shadow(show=False)

        SUBJECTS = [
            HEP_Subject(
                f'EP1163_{x}',
                [
                    'TEN_SECOND_PILOT'
                    # 'TEN_MINUTE_TEST'
                    # 'FULL'
                ][0], [
                    # (ManualPeakDetection, inf, 'CALC'),
                    None,
                    (ECGLAB_Original, inf, 'CALC'),
                    (ECGLAB_Original, inf, 'CALC'),
                    # (ecglab_fast, inf, 'CALC'),
                    # (ecglab_slow, inf, 'CALC'),
                    # (pan_tompkins, inf, 'CALC'),
                ][x],
                (2, 5)  # (555,562)
            ) for x in range(1, 2)
        ]

        for sub in SUBJECTS:  # build shadow docs
            sub.rPeaks  # build shadow docs

        if SUBJECTS[0].times()[-1] > 602:
            HR_ASSERTION_THRESH = 1.33  # Hz Park et. al
            SEC_WIN = 600  # Hz Park et. al
            for sub in SUBJECTS:
                t = sub.times()
                random.seed(sub.mindex)
                start = random.randint(0, int(t[-1] - (SEC_WIN + 2)))
                end = start + SEC_WIN
                beats = sub.rPeaks / sub.Fs
                beats = beats[np.bitwise_and(
                    beats >= start, beats < end
                )]
                beats_per_sec = len(beats) / SEC_WIN
                log(f'heartrate(10min sample) of subject {sub.mindex} = {beats_per_sec}Hz')
                assert beats_per_sec < HR_ASSERTION_THRESH

        if len(SUBJECTS) > 1 and COMPARE_IBI:
            shadow.fig(
                [[plot] for s in SUBJECTS for plot in s.plots()] + [[compare_IBI(SUBJECTS[0], SUBJECTS[1])]]
            )

        if _SAVE_DATA:
            [s.savepeaks() for s in SUBJECTS]
    instructions = ''
    configuration = ''
    credits = 'Isaac, Brain Modulation Lab'
