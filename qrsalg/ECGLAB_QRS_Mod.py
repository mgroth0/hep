from abc import ABC
import math
from numpy import ones
from scipy.signal import bilinear, filtfilt, lfilter

from mlib.boot.stream import arr
from mlib.math import butter
from mlib.term import log_invokation
from mlib.web.html import H1, H3
from mlib.web.shadow import Shadow
from qrsalg.PeakDetectionAlg import PeakDetectionAlg


DOC = Shadow(
    show=True,
    include_index_link=False,
    bib='hep_bib.yml',
    includes=["qrsalg.ecglab_original"]
)

TEST_FILTERS = False
_PLOT_SLICE = slice(1000, None)

class ECGLAB_QRS_Mod(PeakDetectionAlg, ABC):
    # DOC: START
    DOC += H1(
        'R peak detection algorithm - Matt Groth',
        style={'text-align': 'center'}
    )
    DOC.link(
        'based on an algorithm from Perakakis\' HEPLAB',
        '#perakakis2019'
    )
    DOC.link(
        '...which was based on de Carvalho et al\'s algorithm',
        '#carvalho2002'
    )
    DOC.H2(
        'Preprocessing',
        style={'text-align': 'center'}
    )
    @staticmethod
    @log_invokation
    def preprocess(
            ecg,  # raw, unfiltered, no downsampling
            Fs  # (2000 Hz)
    ):
        global DOC

        DOC.plot(
            ecg[_PLOT_SLICE],
            hideYTicks=True,
            title='Raw ECG',
            x=(PLOT_X := ((arr(range(len(ecg))) / Fs)[_PLOT_SLICE])),
            xticklocs=list(range(1, 11)),
            xlabel='seconds'
        )
        DOC += H3(
            '',
            style={'text-align': 'center'}
        )

        # DOC: STOP
        if TEST_FILTERS:
            DOC += H3(
                'Test Filters',
                style={'text-align': 'center'}
            )
            nyq = 0.5 * Fs
            lowcut = 59
            highcut = 61
            low = lowcut / nyq
            high = highcut / nyq
            order = 1

            b, a = butter(order, [low, high], btype='bandstop')

            ecg_test = lfilter(b, a, ecg)
            DOC.plot(
                ecg_test[_PLOT_SLICE],
                hideYTicks=True,
                title='bandstop filter',
                x=PLOT_X,
                xticklocs=list(range(1, 11)),
                xlabel='seconds'
            )
        # DOC: START

        DOC += H3(
            'First Bandpass Filter (low-pass 17 Hz, customized by De Carvalho et al.)',
            style={'text-align': 'center'}
        )
        Q = 3  # optimum ripple length for detection DOC:CITE[carvalho2002]DOC:CITE[perakakis2019]
        k = 1.2  # gain, does not effect detection DOC:CITE[carvalho2002]DOC:CITE[perakakis2019]
        w0 = 17 * 2 * math.pi  # 17 in DOC:CITE[carvalho2002], but DOC:CITE[perakakis2019] is "17.5625 * 2 * math.pi" (why?)
        numerator = k * w0**2  # DOC:CITE[carvalho2002]DOC:CITE[perakakis2019]
        denominator = [1, (w0 / Q), w0**2]  # DOC:CITE[carvalho2002]DOC:CITE[perakakis2019]

        DOC.math(
            'De Carvalho et al.\'s Bandpass Filter Equation',
            r'''
            H(s)=\frac{kw_0^2}{s^2+(\frac{w_0}{Q})s+w_0^2}
            '''
        )

        z, p = bilinear(numerator, denominator, Fs)
        ecg_flt = filtfilt(z, p, ecg)

        DOC.plot(
            ecg_flt[_PLOT_SLICE],
            hideYTicks=True,
            title='ECG After First Bandpass Filter',
            x=PLOT_X,
            xticklocs=list(range(1, 11)),
            xlabel='seconds'
        )

        ecg_flt = lfilter([1, -1], 1, ecg_flt)  # Derivative Filter  DOC:CITE[carvalho2002]DOC:CITE[perakakis2019]

        DOC.plot(
            ecg_flt[_PLOT_SLICE],  # removing 0.1 sec from from beginning to fix axis
            hideYTicks=True,
            title='ECG After Derivative Filter',
            x=PLOT_X,  # removing 0.1 sec from from beginning to fix axis
            xticklocs=list(range(1, 11)),
            xlabel='seconds'
        )

        DOC += H3(
            'Second Bandpass Filter (low-pass 30 Hz)',
            style={'text-align': 'center'}
        )

        # 8th order used in cascade avoids high-freq noise amplification DOC:CITE[carvalho2002]DOC:CITE[perakakis2019]
        [z, p] = butter(8, 30 / (Fs / 2))
        ecg_flt = lfilter(z, p, ecg_flt)

        DOC.plot(
            ecg_flt[_PLOT_SLICE],
            hideYTicks=True,
            title='ECG After Second Bandpass Filter',
            x=PLOT_X,
            xticklocs=list(range(1, 11)),
            xlabel='seconds'
        )

        DOC += H3(
            'Normalization?',
            style={'text-align': 'center'}
        )

        ecg_flt = ecg_flt / max(abs(ecg_flt))  # unsure why Perakakis added this DOC:CITE[perakakis2019]

        DOC.plot(
            ecg_flt[_PLOT_SLICE],
            hideYTicks=True,
            title='ECG After Normalization? (from Perakakis)',
            x=PLOT_X,
            xticklocs=list(range(1, 11)),
            xlabel='seconds'
        )

        DOC += H3(
            'Squaring',
            style={'text-align': 'center'}
        )

        ecg_flt = ecg_flt**2  # makes every sample positive so threshold detector will work DOC:CITE[carvalho2002]DOC:CITE[perakakis2019]

        DOC.plot(
            ecg_flt[_PLOT_SLICE],
            hideYTicks=True,
            title='ECG After Squaring',
            x=PLOT_X,
            xticklocs=list(range(1, 11)),
            xlabel='seconds'
        )

        DOC += H3(
            'Integration',
            style={'text-align': 'center'}
        )

        # Integration was not in original De Carvalho algorithm. Unsure why Perakakis added this DOC:CITE[perakakis2019]
        N = round(0.150 * Fs)
        ecg_flt = 1 / N * lfilter(ones(N), 1, ecg_flt)

        DOC.plot(
            ecg_flt[_PLOT_SLICE],
            hideYTicks=True,
            title='Final Preprocessed ECG (After Integration)',
            x=PLOT_X,
            xticklocs=list(range(1, 11)),
            xlabel='seconds'
        )

        return ecg_flt
