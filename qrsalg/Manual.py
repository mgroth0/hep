from mlib.boot.stream import arr, ints
from mlib.file import File
from mlib.math import nopl_high
from mlib.proj.struct import vers
from qrsalg.PeakDetectionAlg import PeakDetectionAlg, find_local_maxima
class ManualPeakDetection(PeakDetectionAlg):
    MANUAL_INPUT_FILE = File('_data/EP1163_10min_ManInput.mat')
    def preprocess(self, ecg, Fs):
        return nopl_high(ecg, Fs)
    def rpeak_detect(self, ecg_raw, Fs, ecg_flt, ecg_raw_nopl_high):
        # just fixpeaks
        qrs = arr(self.MANUAL_INPUT_FILE['heartbeatevents']['py'][0]).flatten()[0].flatten()
        qrs = ints(qrs)
        qrs = qrs[qrs >= self.rawslice.start]
        qrs = qrs[qrs < self.rawslice.stop]
        if vers(self.version) >= vers(1):
            qrs = find_local_maxima(
                qrs,
                ecg_flt,
                AUTO=True,
                CROP_FIRST_LAST=True
            )
        return qrs
