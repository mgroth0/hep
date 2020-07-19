import importlib

from abc import ABC, abstractmethod

from numpy import inf
from matplotlib import pyplot as plt

from mlib.boot.lang import composed, isint, num2str, strcmp
from mlib.boot.mlog import log, disp
from mlib.boot.stream import flat, itr, mymax
from mlib.err import assert_int
from mlib.inspect import mn
from mlib.term import Progress, log_invokation


class PeakDetectionAlg(ABC):
    def __init__(self, version=inf):
        log('creating Algorithm: $$', self, version)
        if version == inf:
            from packaging import version
            version = max(self.versions().keys(), key=lambda k: version.parse(k))
        self.version = version

    @classmethod
    def versions(cls):
        vm = importlib.import_module(
            f'{mn(cls)}_versions'
        )
        return vm.VERSIONS

    @composed(abstractmethod, log_invokation)
    def preprocess(self, ecg, Fs): pass

    @composed(abstractmethod, log_invokation)
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

def find_local_maxima(
        r_indices,
        ecg_flt,
        FIX_WIDTH=100,
        CROP_FIRST_LAST=False,
        AUTO=True,
        ABS=True
):
    # (searchback)
    if isint(FIX_WIDTH):
        FIX_WIDTH = (FIX_WIDTH, FIX_WIDTH)

    if ABS:
        myabs = abs
    else:
        myabs = lambda x: x

    r_indices = flat(r_indices)
    y = []
    for i in itr(r_indices):
        y.append(ecg_flt[r_indices[i]])

    newlats = r_indices
    marks = []
    if AUTO:
        log('automatically fixing all heartbeats')
    with Progress(len(r_indices), 'searching back on', 'marks') as prog:
        for i in itr(r_indices):
            if CROP_FIRST_LAST and (i == 0 or i == len(r_indices) - 1):
                continue

            fix_width_back = min(FIX_WIDTH[0], r_indices[0])
            fix_width_forward = FIX_WIDTH[1]

            the_lat = assert_int(r_indices[i])
            mn = the_lat - fix_width_back
            mx = the_lat + 1 + fix_width_forward

            if len(ecg_flt) >= mx:
                snippet = ecg_flt[mn:mx]
            else:
                snippet = ecg_flt[mn:len(ecg_flt)]

            [M, I] = mymax(myabs(snippet))
            fixed_lat = the_lat + I - fix_width_back

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
            prog.tick()
    return newlats
