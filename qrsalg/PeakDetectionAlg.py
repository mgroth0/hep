from abc import ABC, abstractmethod
import math

from numpy import ones
from scipy.signal import bilinear, filtfilt
from matplotlib import pyplot as plt

from defaults import *


class PeakDetectionAlg(ABC):
    def __init__(self, version=inf):
        log('creating Algorithm: $$', self, version)
        if version == inf:
            version = max(self.versions().keys())
        self.version = version

    @classmethod
    @abstractmethod
    def versions(cls):
        pass

    @composed(abstractmethod, logverb)
    def preprocess(self, ecg, Fs):
        pass

    @composed(abstractmethod, logverb)
    def rpeak_detect(self, ecg_raw, Fs, ecg_flt):
        pass

    def name(self):
        return self.abr() + '_' + str(self.version).replace('.','_')

    @staticmethod
    def standardPP(ecg,Fs):
        log('filter')
        [B, A] = butter(4, 1 / (Fs / 2), 'high')  # cf = 1 Hz
        ecg_flt2 = filtfilt(B, A, ecg)

        # ecg_flt2 = ecg_flt2

        ecg_flt2 = bandstop(ecg_flt2, 59, 61, Fs, 1)

        #         just for plot visibility
        ecg_flt2 = (20 * ecg_flt2) + 0.01
        return ecg_flt2

    @classmethod
    def abr(cls):
        import pan_tompkins
        import ecglab_fast
        import ecglab_slow
        # noinspection PyTypeChecker
        return {
            pan_tompkins.pan_tompkins: 'pan',
            ecglab_fast.ecglab_fast  : 'fast',
            ecglab_slow.ecglab_slow  : 'slow',
            ManualPeakDetection      : 'manual'
        }[cls]

    def fixpeaks(self, r_indices, ecg_flt, AUTO=True):

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
            if i == 0 or i == len(r_indices) -1:
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

class HEPLAB_Alg(PeakDetectionAlg, ABC):
    def preprocess(self, ecg, Fs):
        log('Filter at 17Hz')
        Q = 3
        gain = 1.2
        w0 = 17.5625 * 2 * math.pi
        NUM = gain * (w0 ** 2)
        DEN = [1, (w0 / Q), w0 ** 2]
        [B, A] = bilinear(NUM, DEN, Fs)

        ecg_flt = filtfilt(B, A, ecg)

        ecg_flt = lfilter([1, -1], 1, ecg_flt)

        log('low-pass 30 Hz')
        [B, A] = butter(8, 30 / (Fs / 2))
        ecg_flt = lfilter(B, A, ecg_flt)
        ecg_flt = ecg_flt / max(abs(ecg_flt))

        ecg_flt = ecg_flt ** 2

        log('integration')
        N = round(0.150 * Fs)
        ecg_flt = 1 / N * lfilter(ones(N), 1, ecg_flt)

        self.ecg_flt2 = self.standardPP(ecg,Fs)

        return ecg_flt

class JustPreprocess(HEPLAB_Alg):
    @classmethod
    def versions(cls): return {1: 'init'}
    def rpeak_detect(self, ecg_raw, fs, ecg_flt): return -1

class ManualPeakDetection(PeakDetectionAlg):
    @classmethod
    def versions(cls): return {
        1  : 'init',
        1.1: 'fixPeaks'
    }
    MANUAL_FILE =File('HEP/data/EP1163_10min_qrs_manual.mat')
    def preprocess(self, ecg, Fs):
        return self.standardPP(ecg,Fs)
    def rpeak_detect(self, ecg_raw, Fs, ecg_flt):
        qrs = arr(self.MANUAL_FILE['heartbeatevents']['py'][0][0]).flatten()
        if self.version >= 1:
            qrs = self.fixpeaks(qrs,ecg_flt,AUTO=True)
        return qrs
