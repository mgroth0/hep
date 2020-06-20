from abc import ABC
import math

from numpy import ones
from scipy.signal import bilinear, filtfilt, lfilter, butter

from mlib.boot.mlog import log
from qrsalg.PeakDetectionAlg import PeakDetectionAlg
class HEPLAB_Alg(PeakDetectionAlg, ABC):
    def preprocess(self, ecg, Fs):
        log('Filter at 17Hz')
        Q = 3
        gain = 1.2
        w0 = 17.5625 * 2 * math.pi
        NUM = gain * (w0**2)
        DEN = [1, (w0 / Q), w0**2]
        [B, A] = bilinear(NUM, DEN, Fs)

        ecg_flt = filtfilt(B, A, ecg)

        ecg_flt = lfilter([1, -1], 1, ecg_flt)

        log('low-pass 30 Hz')
        [B, A] = butter(8, 30 / (Fs / 2))
        ecg_flt = lfilter(B, A, ecg_flt)
        ecg_flt = ecg_flt / max(abs(ecg_flt))

        ecg_flt = ecg_flt**2

        log('integration')
        N = round(0.150 * Fs)
        ecg_flt = 1 / N * lfilter(ones(N), 1, ecg_flt)

        self.ecg_flt2 = self.standardPP(ecg, Fs)

        return ecg_flt
class JustPreprocess(HEPLAB_Alg):
    @classmethod
    def versions(cls): return {'1': 'init'}
    def rpeak_detect(self, ecg_raw, fs, ecg_flt): return -1