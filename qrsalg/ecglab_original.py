from matplotlib.lines import Line2D

from mlib.boot import log
from mlib.boot.stream import arr, find, bitwise_and, ints
from mlib.fig.PlotData import MultiPlot, PlotData
from mlib.math import unitscale_demean, unitscale_demean_fun
from mlib.term import log_invokation, Progress
from mlib.web.shadow import Shadow
from qrsalg.ECGLAB_QRS_Mod import ECGLAB_QRS_Mod, _PLOT_SLICE, _PLOT_SLICE_SMALL
from qrsalg.PeakDetectionAlg import find_local_maxima
import numpy as np
DOC = Shadow(
    bib='hep_bib.yml',
    include_index_link=False,
)

# TODO: "original" is the goal, but currently its just HEPLAB_fast
class ECGLAB_Original(ECGLAB_QRS_Mod):

    @log_invokation
    def rpeak_detect(
            self,
            ecg_raw,
            Fs,
            ecg_flt,
            ecg_raw_nopl_high
    ):
        return self.detect_rpeaks(
            Fs,
            ecg_flt,
            ecg_raw_nopl_high
        )

    # DOC: START

    DOC.H2(
        'R Peak Detection',
        style={'text-align': 'center'}
    )



    @staticmethod
    @log_invokation
    def detect_rpeaks(
            Fs,
            ecg_flt,  # output of preprocess()
            ecg_raw_nopl_high  # output of nopl_high()
    ):
        DOC.fig(
            [[MultiPlot(
                PlotData(
                    unitscale_demean(ecg_flt[_PLOT_SLICE]),
                    hideYTicks=True,
                    item_type='line',
                    title='ECG Signals',
                    x=(PLOT_X := ((arr(range(len(ecg_flt))) / Fs)[_PLOT_SLICE])),
                    xticklocs=list(range(1, 11)),
                    xlabel='seconds'
                ),
                PlotData(
                    unitscale_demean(ecg_raw_nopl_high[_PLOT_SLICE]),
                    hideYTicks=True,
                    item_type='line',
                    item_color='r',
                    x=PLOT_X,
                ),
                legend=[
                    Line2D([0], [0], color='w', lw=4, label='ect_flt'),
                    Line2D([0], [0], color='r', lw=4, label='ecg_raw_nopl_high'),
                ]
            )]]
        )

        DOC.fig(
            [[MultiPlot(
                PlotData(
                    unitscale_demean(ecg_flt[_PLOT_SLICE_SMALL]),
                    hideYTicks=True,
                    item_type='line',
                    title='ECG Signals -- zoomed in',
                    x=(PLOT_X_SMALL := ((arr(range(len(ecg_flt))) / Fs)[_PLOT_SLICE_SMALL])),
                    xticklocs=list(range(1, 11)),
                    xlabel='seconds'
                ),
                PlotData(
                    unitscale_demean(ecg_raw_nopl_high[_PLOT_SLICE_SMALL]),
                    hideYTicks=True,
                    item_type='line',
                    item_color='r',
                    x=PLOT_X_SMALL,
                ),
                legend=[
                    Line2D([0], [0], color='w', lw=4, label='ect_flt'),
                    Line2D([0], [0], color='r', lw=4, label='ecg_raw_nopl_high'),
                ]
            )]]
        )

        DOC.H3(
            'Adaptive Threshold Detector',
            style={'text-align': 'center'}
        )

        THRESH = 0.15  # threshold for peak detection DOC:CITE[perakakis2019]
        THRESH_ADAPT_WIN_WIDTH = round(2 * Fs)  # 2 sec DOC:CITE[perakakis2019]
        ART_THRESH_ADAPT_WIN_WIDTH = round(0.2 * Fs)  # this is for the new artifact detection mechanism below

        STEP = round(0.350 * Fs)  # minimum interval between marks (350ms) DOC:CITE[carvalho2002]DOC:CITE[perakakis2019]
        STEP_SMALL = round(0.01 * Fs)  # 10ms step DOC:CITE[perakakis2019]

        # initiate variables
        sz = len(ecg_flt)  # size of signal
        n = 0  # current sample index
        r_peak_indices = []  # where detected R peak indices are stored

        safe_lmt = 0.0  # holds the "safe" threshold, used in an original artifact detection mechanism detailed below

        # DOC: STOP
        made_loop_fig = False
        with Progress(sz, 'scanning', 'samples') as prog:
            # DOC: START
            while n + 1 < sz:  # scan entire signal
                comp_area = ecg_flt[  # the regular window for threshold calculation
                            max(0, n - THRESH_ADAPT_WIN_WIDTH):
                            min(n + THRESH_ADAPT_WIN_WIDTH, sz)
                            ]
                local_comp_area = ecg_flt[  # the small window for for artifact detection
                                  max(0, n - ART_THRESH_ADAPT_WIN_WIDTH):
                                  min(n + ART_THRESH_ADAPT_WIN_WIDTH, sz)
                                  ]

                lmt = THRESH * max(abs(comp_area))  # R peak threshold
                local_lmt = THRESH * max(abs(local_comp_area))  # artifact threshold

                # DOC: STOP
                if not made_loop_fig and n > 5000:
                    made_loop_fig = True
                    fig_slice = slice(n - THRESH_ADAPT_WIN_WIDTH, n + THRESH_ADAPT_WIN_WIDTH)
                    # DOC: START
                    DOC.fig(
                        [[MultiPlot(
                            PlotData(
                                ecg_flt[fig_slice],
                                hideYTicks=True,
                                item_type='line',
                                title='R Peak Detection Window and Threshold',
                                x=(arr(range(len(ecg_flt))) / Fs)[fig_slice],
                                xticklocs=list(range(1, 11)),
                                xlabel='seconds'
                            ),
                            PlotData(
                                arr([lmt] * ecg_flt[fig_slice].size),
                                hideYTicks=True,
                                item_type='line',
                                item_color='y',
                                x=(arr(range(len(ecg_flt))) / Fs)[fig_slice],
                                xticklocs=list(range(1, 11)),
                                xlabel='seconds'
                            ),
                            legend=[
                                Line2D([0], [0], color='w', lw=4, label='ect_flt'),
                                Line2D([0], [0], color='y', lw=4, label='lmt')
                            ]
                        )]]
                    )

                if lmt > 1.5 * safe_lmt and safe_lmt != 0.0:
                    # This original check notices when the threshold suddenly jumps. In my tests I found this to only detect large artifacts
                    lmt = safe_lmt  # since an artifact was detected, use the old "safe" threshold
                    safe_lmt *= 1.001  # increment the acceptable threshold gradually to eventually rejoin lmt
                else:
                    safe_lmt = lmt  # no artifact was detected, so store this threshold in case it should be used next time

                if local_lmt > 2 * lmt:  # another original artifact detection mechanism
                    # if the local threshold is much larger than the normal one, use the local one instead
                    # this should help adjust the location of some detected peaks when the peak was very large
                    lmt = local_lmt

                if (ecg_flt[n] > lmt) and (n + 1 < sz):
                    r_peak_indices.append(n)  # this n passed the threshod, so add it to the stored r peaks
                    n += STEP  # advance 350 ms and start scanning the next cardiac cycle
                else:
                    n += STEP_SMALL  # jump 10 ms forward

                # DOC: STOP
                prog.tick(n)
                # DOC: START

        # DOC: STOP
        fig_indices_indices = ints(np.nonzero(
            arr(r_peak_indices) >= _PLOT_SLICE.start
        )[0])
        fig_indices_indices_small = ints(np.nonzero(bitwise_and(
            arr(r_peak_indices) >= _PLOT_SLICE_SMALL.start,
            arr(r_peak_indices) <= _PLOT_SLICE_SMALL.stop
        ))[0])
        r_peak_indices_fig = arr(r_peak_indices)[fig_indices_indices]
        r_peak_indices_small_fig = arr(r_peak_indices)[fig_indices_indices_small]
        # DOC: START
        DOC.fig(
            [[MultiPlot(
                PlotData(
                    unitscale_demean(ecg_flt[_PLOT_SLICE]),
                    hideYTicks=True,
                    item_type='line',
                    title='First Detected Peaks',
                    x=PLOT_X,
                    xticklocs=list(range(1, 11)),
                    xlabel='seconds'
                ),
                PlotData(
                    unitscale_demean(ecg_raw_nopl_high[_PLOT_SLICE]),
                    hideYTicks=True,
                    item_type='line',
                    item_color='r',
                    x=PLOT_X,
                ),
                PlotData(
                    item_type='scatter',
                    hideYTicks=True,
                    item_color='b',
                    y=unitscale_demean_fun(ecg_flt[_PLOT_SLICE])(ecg_flt)[r_peak_indices_fig],
                    x=r_peak_indices_fig / Fs
                ),
                legend=[
                    Line2D([0], [0], color='w', lw=4, label='ect_flt'),
                    Line2D([0], [0], color='r', lw=4, label='ecg_raw_nopl_high'),
                ]
            )]]
        )
        DOC.fig(
            [[MultiPlot(
                PlotData(
                    unitscale_demean(ecg_flt[_PLOT_SLICE_SMALL]),
                    hideYTicks=True,
                    item_type='line',
                    title='First Detected Peaks -- zoomed in',
                    x=PLOT_X_SMALL,
                    xticklocs=list(range(1, 11)),
                    xlabel='seconds'
                ),
                PlotData(
                    unitscale_demean(ecg_raw_nopl_high[_PLOT_SLICE_SMALL]),
                    hideYTicks=True,
                    item_type='line',
                    item_color='r',
                    x=PLOT_X_SMALL,
                ),
                PlotData(
                    item_type='scatter',
                    hideYTicks=True,
                    item_color='b',
                    y=unitscale_demean_fun(ecg_flt[_PLOT_SLICE_SMALL])(ecg_flt)[r_peak_indices_small_fig],
                    x=r_peak_indices_small_fig / Fs
                ),
                legend=[
                    Line2D([0], [0], color='w', lw=4, label='ect_flt'),
                    Line2D([0], [0], color='r', lw=4, label='ecg_raw_nopl_high'),
                ]
            )]]
        )

        DOC.H3(
            'Return to Signal',
            style={'text-align': 'center'}
        )
        RETURN = round(0.030 * Fs)  # Not sure where DOC:CITE[perakakis2019] got this number
        r_peak_indices = arr(r_peak_indices) - RETURN  # DOC:CITE[perakakis2019] probably was fixing delayed peaks

        # DOC: STOP
        fig_indices_indices = ints(np.nonzero(
            arr(r_peak_indices) >= _PLOT_SLICE.start
        )[0])
        fig_indices_indices_small = ints(np.nonzero(bitwise_and(
            arr(r_peak_indices) >= _PLOT_SLICE_SMALL.start,
            arr(r_peak_indices) <= _PLOT_SLICE_SMALL.stop
        ))[0])
        r_peak_indices_fig = arr(r_peak_indices)[fig_indices_indices]
        r_peak_indices_small_fig = arr(r_peak_indices)[fig_indices_indices_small]
        # DOC: START
        DOC.fig(
            [[MultiPlot(
                PlotData(
                    unitscale_demean(ecg_flt[_PLOT_SLICE]),
                    hideYTicks=True,
                    item_type='line',
                    title='Detected Peaks After Return',
                    x=PLOT_X,
                    xticklocs=list(range(1, 11)),
                    xlabel='seconds'
                ),
                PlotData(
                    unitscale_demean(ecg_raw_nopl_high[_PLOT_SLICE]),
                    hideYTicks=True,
                    item_type='line',
                    item_color='r',
                    x=PLOT_X,
                ),
                PlotData(
                    item_type='scatter',
                    hideYTicks=True,
                    item_color='b',
                    y=unitscale_demean_fun(ecg_flt[_PLOT_SLICE])(ecg_flt)[r_peak_indices_fig],
                    x=r_peak_indices_fig / Fs
                ),
                legend=[
                    Line2D([0], [0], color='w', lw=4, label='ect_flt'),
                    Line2D([0], [0], color='r', lw=4, label='ecg_raw_nopl_high'),
                ]
            )]]
        )
        DOC.fig(
            [[MultiPlot(
                PlotData(
                    unitscale_demean(ecg_flt[_PLOT_SLICE_SMALL]),
                    hideYTicks=True,
                    item_type='line',
                    title='Detected Peaks After Return -- zoomed in',
                    x=PLOT_X_SMALL,
                    xticklocs=list(range(1, 11)),
                    xlabel='seconds'
                ),
                PlotData(
                    unitscale_demean(ecg_raw_nopl_high[_PLOT_SLICE_SMALL]),
                    hideYTicks=True,
                    item_type='line',
                    item_color='r',
                    x=PLOT_X_SMALL,
                ),
                PlotData(
                    item_type='scatter',
                    hideYTicks=True,
                    item_color='b',
                    y=unitscale_demean_fun(ecg_flt[_PLOT_SLICE_SMALL])(ecg_flt)[r_peak_indices_small_fig],
                    x=r_peak_indices_small_fig / Fs
                ),
                legend=[
                    Line2D([0], [0], color='w', lw=4, label='ect_flt'),
                    Line2D([0], [0], color='r', lw=4, label='ecg_raw_nopl_high'),
                ]
            )]]
        )

        DOC.H3(
            'Find Local Maxima',
            style={'text-align': 'center'}
        )

        # searchback algorithm: adjust peaks to local maxima DOC:CITE[carvalho2002]DOC:CITE[perakakis2019]
        AREA = round(0.070 * Fs)  # local maxima window
        r_peak_indices = find_local_maxima(
            r_peak_indices,
            ecg_raw_nopl_high,  # we only use the "original" signal here
            FIX_WIDTH=(8, AREA)
        )


        # DOC: STOP
        fig_indices_indices = ints(np.nonzero(
            arr(r_peak_indices) >= _PLOT_SLICE.start
        )[0])
        fig_indices_indices_small = ints(np.nonzero(bitwise_and(
            arr(r_peak_indices) >= _PLOT_SLICE_SMALL.start,
            arr(r_peak_indices) <= _PLOT_SLICE_SMALL.stop
        ))[0])
        r_peak_indices_fig = arr(r_peak_indices)[fig_indices_indices]
        r_peak_indices_small_fig = arr(r_peak_indices)[fig_indices_indices_small]
        # DOC: START
        DOC.fig(
            [[MultiPlot(
                PlotData(
                    unitscale_demean(ecg_raw_nopl_high[_PLOT_SLICE]),
                    title='R Peaks After Found Local Maxima',
                    hideYTicks=True,
                    item_type='line',
                    item_color='r',
                    x=PLOT_X,
                ),
                PlotData(
                    item_type='scatter',
                    hideYTicks=True,
                    item_color='b',
                    y=unitscale_demean_fun(ecg_raw_nopl_high[_PLOT_SLICE])(ecg_raw_nopl_high)[r_peak_indices_fig],
                    x=r_peak_indices_fig / Fs
                ),
                legend=[
                    Line2D([0], [0], color='w', lw=4, label='ect_flt'),
                    Line2D([0], [0], color='r', lw=4, label='ecg_raw_nopl_high'),
                ]
            )]]
        )
        DOC.fig(
            [[MultiPlot(
                PlotData(
                    unitscale_demean(ecg_raw_nopl_high[_PLOT_SLICE_SMALL]),
                    title='R Peaks After Found Local Maxima -- zoomed',
                    hideYTicks=True,
                    item_type='line',
                    item_color='r',
                    x=PLOT_X_SMALL,
                ),
                PlotData(
                    item_type='scatter',
                    hideYTicks=True,
                    item_color='b',
                    y=unitscale_demean_fun(ecg_raw_nopl_high[_PLOT_SLICE_SMALL])(ecg_raw_nopl_high)[r_peak_indices_small_fig],
                    x=r_peak_indices_small_fig / Fs
                ),
                legend=[
                    Line2D([0], [0], color='w', lw=4, label='ect_flt'),
                    Line2D([0], [0], color='r', lw=4, label='ecg_raw_nopl_high'),
                ]
            )]]
        )


        return r_peak_indices


DOC.write_bib()
