from abc import ABC
import math

from numpy import ones
from scipy.signal import bilinear, filtfilt, lfilter, butter
from matplotlib import pyplot as plt

from bib import bib_data, bib2html
from mlib.boot.mutil import log_invokation
from mlib.proj.struct import PROJ
from mlib.web.shadow import Shadow, AutoHTMLImage
from qrsalg.PeakDetectionAlg import PeakDetectionAlg

DOC = Shadow()

# DOC: LINK:Original ECGLAB Paper,https://u.nu/qy-4k
class ECGLAB_QRS_Mod(PeakDetectionAlg, ABC):
    @log_invokation()
    # DOC: START
    def preprocess(self, ecg, Fs):
        with plt.style.context('dark_background'):
            plt.plot(ecg)
            PROJ.RESOURCES_FOLDER.mkdirs()['figs/qrsalg'].mkdirs()
            im_file = PROJ.RESOURCES_FOLDER['figs/qrsalg/ECGLAB_QRS_Mod1.png']
            plt.savefig(im_file.abspath)
        DOC.children += [AutoHTMLImage(im_file)]
        DOC.children += [bib2html(bib_data)]
        #################
        # Bandpass Filter
        #################
        Q = 3  # optimum ripple length for detection
        k = 1.2  # gain, does not effect detection
        # FixMe: * 2 * math.pi... why?
        w0 = 17 * 2 * math.pi
        numerator = k * w0**2
        denominator = [1, (w0 / Q), w0**2]

        # matplotlib.rcParams['text.usetex'] = True
        plt.clf()
        with plt.style.context('dark_background'):
            plt.text(
                x=0.5,
                y=0.5,
                s='whatever'
                # s='$\displaystyle\sum_{n=1}^\infty'
                #   r'\frac{-e^{i\pi}}{2^n}$'
            )
            PROJ.RESOURCES_FOLDER.mkdirs()['figs/qrsalg'].mkdirs()
            im_file = PROJ.RESOURCES_FOLDER['figs/qrsalg/ECGLAB_QRS_Mod2.png']
            plt.savefig(im_file.abspath)
        DOC.children += [AutoHTMLImage(im_file)]
        # matplotlib.rcParams['text.usetex'] = False

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
