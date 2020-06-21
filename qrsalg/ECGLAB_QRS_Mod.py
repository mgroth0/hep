from abc import ABC
import math

from numpy import ones
from scipy.signal import bilinear, filtfilt, lfilter, butter

from mlib.boot.mutil import log_invokation
from mlib.web.web import Shadow
from qrsalg.PeakDetectionAlg import PeakDetectionAlg

DOC = Shadow()

# SOURCE: https://u.nu/qy-4k
class ECGLAB_QRS_Mod(PeakDetectionAlg, ABC):
    @log_invokation()
    def preprocess(self, ecg, Fs):
        DOC.children += ["Hello World!"]
        #################
        # Bandpass Filter
        #################
        Q = 3  # optimum ripple length for detection
        k = 1.2  # gain, does not effect detection
        # FixMe: * 2 * math.pi... why?
        w0 = 17 * 2 * math.pi
        numerator = k * w0**2
        denominator = [1, (w0 / Q), w0**2]
        z, p = bilinear(numerator, denominator, Fs)

        ecg_flt = filtfilt(z, p, ecg)
        ecg_flt = lfilter([1, -1], 1, ecg_flt)
        # low-pass 30 Hz
        [z, p] = butter(8, 30 / (Fs / 2))
        ecg_flt = lfilter(z, p, ecg_flt)
        ecg_flt = ecg_flt / max(abs(ecg_flt))
        ecg_flt = ecg_flt**2
        # integration
        N = round(0.150 * Fs)
        return 1 / N * lfilter(ones(N), 1, ecg_flt)
