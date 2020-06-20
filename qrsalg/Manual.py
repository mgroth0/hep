from mlib.boot.mutil import File, arr, ints, vers
from qrsalg.PeakDetectionAlg import PeakDetectionAlg
class ManualPeakDetection(PeakDetectionAlg):
    @classmethod
    def versions(cls): return {
        '1'  : 'init',
        '1.1': 'fixPeaks'
    }
    MANUAL_INPUT_FILE = File('_data/EP1163_10min_ManInput.mat')
    def preprocess(self, ecg, Fs):
        return self.standardPP(ecg, Fs)
    def rpeak_detect(self, ecg_raw, Fs, ecg_flt):
        # just fixpeaks
        qrs = arr(self.MANUAL_INPUT_FILE['heartbeatevents']['py'][0]).flatten()[0].flatten()
        qrs = ints(qrs)
        qrs = qrs[qrs >= self.rawslice.start]
        qrs = qrs[qrs < self.rawslice.stop]
        if vers(self.version) >= vers(1):
            qrs = self.fixpeaks(qrs, ecg_flt, AUTO=True)
        return qrs
