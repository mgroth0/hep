from abc import ABC, abstractmethod

from numpy import inf
from matplotlib import pyplot as plt

from mlib.boot.mlog import log
from mlib.boot.mutil import logverb, composed, flat, itr, assert_int, mymax, num2str, strcmp, disp


class PeakDetectionAlg(ABC):
    def __init__(self, version=inf):
        log('creating Algorithm: $$', self, version)
        if version == inf:
            from packaging import version
            version = max(self.versions().keys(), key=lambda k: version.parse(k))
        self.version = version

    @classmethod
    @abstractmethod
    def versions(cls): pass

    @composed(abstractmethod, logverb)
    def preprocess(self, ecg, Fs): pass

    @composed(abstractmethod, logverb)
    def rpeak_detect(self, ecg_raw, Fs, ecg_flt, ecg_raw_nopl_high): pass

    def name(self):
        return f"{self.abr()}_{str(self.version).replace('.', '_')}"

    @classmethod
    def abr(cls):
        from qrsalg import pan_tompkins
        from qrsalg import ECGLAB_Original
        from qrsalg import ecglab_slow
        from qrsalg import ManualPeakDetection
        # noinspection PyTypeChecker
        return {
            pan_tompkins       : 'pan',
            ECGLAB_Original    : 'fast',
            ecglab_slow        : 'slow',
            ManualPeakDetection: 'manual'
        }[cls]

    def fixpeaks(self, r_indices, ecg_flt, AUTO=True):
        # (searchback)
        FIX_WIDTH = 100

        r_indices = flat(r_indices)
        y = []
        for i in itr(r_indices):
            y.append(ecg_flt[r_indices[i]])

        newlats = r_indices
        marks = []
        if AUTO:
            log('automatically fixing all heartbeats')
        for i in itr(r_indices):
            if i == 0 or i == len(r_indices) - 1:
                continue
            the_lat = assert_int(r_indices[i])
            mn = the_lat - FIX_WIDTH
            mx = the_lat + 1 + FIX_WIDTH
            snippet = ecg_flt[mn:mx]
            [M, I] = mymax(snippet)
            fixed_lat = the_lat + I - FIX_WIDTH
            if M != ecg_flt[the_lat]:
                if not AUTO:
                    log('i=' + num2str(i) + '/' + num2str(len(r_indices)))
                    plt.plot(ecg_flt)
                    plt.scatter([r_indices[i], fixed_lat], [y[i], M], [], [[1, 0, 0], [0, 0, 1]])
                    plt.xlim([mn, mx])
                    plt.show()
                    s = input('fix?(y/n)')
                else:
                    s = 'y'

                if strcmp(s, 'y'):
                    if not AUTO:
                        disp('fixing')
                    newlats[i] = fixed_lat
                    marks = [marks, the_lat]
                else:
                    disp('skipping')
        return newlats
