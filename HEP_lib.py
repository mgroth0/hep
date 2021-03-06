import functools

from numpy import double, diff

from mlib.boot.lang import isinstsafe
from mlib.boot.stream import arr, itr, ints
from mlib.err import assert_int
from mlib.fig.PlotData import PlotData, MultiPlot
from mlib.boot.mlog import log
from mlib.file import File
from mlib.math import nopl_high, nopl
from qrsalg.ECGLAB_QRS_Mod import ECGLAB_QRS_Mod
class MNE_Set_Wrapper:
    def __init__(self, mne_set):
        self.mne_set = mne_set
        self.Fs = assert_int(mne_set.info['sfreq'])
        self.channels = mne_set.info['ch_names']
        self.ECG_CHAN = self.channels.index('C126') if len(self.channels) > 1 else 0
        log('loaded mne data: Fs=$', self.Fs)

    def times(self, item=slice(None)):
        return self.mne_set[0, item][1]

    def __getitem__(self, item):
        data, times = self.mne_set[item[0], item[1]]
        return double(data).flatten()




def HEP_Data(filename):
    return HEP_DATA_FOLDER.resolve(filename)

# HEP_DATA_FOLDER = SyncedDataFolder('_data', '/home/matt/data/HEP')
HEP_DATA_FOLDER = File('_data')





class HEP_Subject:
    def __init__(self, sub_id, dataset, alg, rand_slice):
        self.id = sub_id
        self.mindex = self.id.split('_')[-1]
        self.mindex = int(self.mindex)
        assert self.mindex > 0
        self.rawfile = HEP_Data(sub_id + '.edf')
        self.alg = alg[0](version=alg[1])
        self.algmode = alg[2]
        self.peakfile = HEP_Data(
            {
                'TEN_SECOND_PILOT': sub_id + '_10sec_qrs',
                'TEN_MINUTE_TEST' : sub_id + '_10min_qrs',
                'FULL'            : sub_id + '_qrs'
            }[dataset] + '.mat')
        self.rawslice = {
            'TEN_SECOND_PILOT': slice(0, 20000),
            'TEN_MINUTE_TEST' : slice(0, 1200000),
            'FULL'            : slice(0, None),
        }[dataset]
        self.RAND_SLICE = slice(rand_slice[0] * self.Fs, rand_slice[1] * self.Fs)
    @property
    @functools.lru_cache()
    def raw(self):
        raw = self.rawfile.load()
        return raw
    @property
    @functools.lru_cache()
    def Fs(self):
        return self.raw.Fs
    @property
    @functools.lru_cache()
    def ecg(self):
        return self.raw[self.raw.ECG_CHAN, self.rawslice]
    def _loadpeaks(self):
        rPeaks = self.peakfile[self.alg.name()]['py'][0][0].flatten()
        rPeaks = rPeaks[rPeaks >= self.rawslice.start]
        if self.rawslice.stop is not None:
            rPeaks = rPeaks[rPeaks < self.rawslice.stop]
        assert len(rPeaks.shape) == 1
        assert len(rPeaks) > 2
        return rPeaks
    def _rpeak_detect(self):
        # ugly coding, but its needed for Manual
        self.alg.rawslice = self.rawslice
        return arr(self.alg.rpeak_detect(self.ecg, self.Fs, self.ecg_flt, self.nopl_high))
    @property
    @functools.lru_cache()
    def rPeaks(self):
        if self.algmode == 'LOAD':
            peaks = self._loadpeaks()
        else:
            peaks = self._rpeak_detect()
        return ints(peaks)

    @property
    @functools.lru_cache()
    def _times(self):
        indices = self.rawslice
        if not isinstance(indices, slice):
            if len(indices) == 0: return arr()
            t = self.raw.times(slice(
                min(indices),
                max(indices) + 1))
            indices = arr(indices) - min(indices)
            t = t[indices]
        else:
            t = self.raw.times(indices)
        return t

    def times(self, indices=None):  # seconds
        if indices is None: indices = self.rawslice
        if not isinstance(indices, slice):
            if len(indices) == 0: return arr()
            t = self._times[slice(
                min(indices),
                max(indices) + 1)]
            indices = arr(indices) - min(indices)
            t = t[indices]
        else:
            t = self._times[indices]
        return t

    @property
    @functools.lru_cache()
    def ecg_flt(self):
        return self.alg.preprocess(self.ecg, self.raw.Fs)
    @property
    @functools.lru_cache()
    def nopl_high(self):
        return nopl_high(self.ecg, self.Fs)
    @property
    @functools.lru_cache()
    def nopl(self):
        return nopl(self.ecg, self.Fs)


    def plot_example_rpeaks(self):
        time_mins = 'time (mins)'
        l = PlotData(
            item_type='line',
            y=self.ecg_flt,
            x=self.times() / 60.0,
            xlim=self.samplesToMins(self.RAND_SLICE),
            xlabel=time_mins,
            ylim='auto',
            hideYTicks=True
        )
        s = PlotData(
            item_type='scatter',
            y=self.ecg_flt[self.rPeaks],
            x=self.samplesToMins(self.rPeaks),
            item_color='b',
            xlim=self.samplesToMins(self.RAND_SLICE),

            title=self.alg.name() + ': example R peaks')
        plots = (l, s)
        if isinstsafe(self.alg, ECGLAB_QRS_Mod):
            l2 = PlotData(
                item_type='line',
                y=self.nopl,
                x=self.times() / 60.0,
                xlim=self.samplesToMins(self.RAND_SLICE),
                xlabel=time_mins,
                ylim='auto',
                item_color='g')
            plots = tuple(list(plots) + [l2])
        t = MultiPlot(*plots)
        return t

    def samplesToMs(self, indices):
        if isinstance(indices, slice):
            r = (arr([indices.start, indices.stop]) / self.Fs) * 1000.0
            r = slice(r[0], r[1])
        else:
            r = (arr(indices) / self.Fs) * 1000.0
        return r

    def samplesToSecs(self, indices):
        if isinstance(indices, slice):
            r = (arr([indices.start, indices.stop]) / self.Fs)
            r = slice(r[0], r[1])
        else:
            r = (arr(indices) / self.Fs)
        return r

    def samplesToMins(self, indices):
        if isinstance(indices, slice):
            r = (arr([indices.start, indices.stop]) / self.Fs) / 60.0
            r = slice(r[0], r[1])
        else:
            r = (arr(indices) / self.Fs) / 60.0
        return r

    def __str__(self):
        return self.id

    def plot_IBIs(self):
        ibi = self.samplesToMs(diff(self.rPeaks))

        l = PlotData(
            item_type='line',
            y=ibi,
            x=self.times(self.rPeaks[1:]) / 60.0,
            title=self.alg.name() + ': IBIs',
            ylabel='IBI (ms)',
            xlabel='time (mins)'
        )
        start = PlotData(
            item_type='line',
            y=[min(ibi, default=0), max(ibi, default=1)],
            x=self.samplesToMins([self.RAND_SLICE.start, self.RAND_SLICE.start]),
            item_color='b',
        )
        stop = PlotData(
            item_type='line',
            y=[min(ibi, default=0), max(ibi, default=1)],
            x=self.samplesToMins([self.RAND_SLICE.stop, self.RAND_SLICE.stop]),
            item_color='b',
        )
        t = MultiPlot(l, start, stop)
        return t


    def savepeaks(self):
        if self.algmode == 'LOAD':
            log('skipping savepeaks for ' + str(self) + ' because data was loaded from file')
            #
            return False

        # obsolete stuff
        # if 'heartbeatevents_py' in self.peakfile.load().keys():
        #     del self.peakfile['heartbeatevents_py']
        #     del self.peakfile['heartbeatevents_mat']

        export = {
            'latency': arr(self.rPeaks) + 1,
            'type'   : ['ECG' for _ in itr(self.rPeaks)],
            'urevent': [i + 1 for i in itr(self.rPeaks)]
        }
        self.peakfile[self.alg.name()] = {
            'alg'            : {
                'name'   : self.alg.__class__.__name__,
                'version': self.alg.version,
                'tag'    : self.alg.versions()[self.alg.version]
            },
            'py'             : arr(self.rPeaks),
            'mat'            : arr(self.rPeaks) + 1,
            'heartbeatevents': export
        }
        self.peakfile['heartbeatevents'] = export
        return True

    def plots(self):
        # diff the qrs of each
        return [
            self.plot_example_rpeaks(),
            self.plot_IBIs()
        ]

def compare_IBI(s1, s2):
    comp = s1.samplesToMs(s2.rPeaks - s1.rPeaks)
    times = s1.times(s1.rPeaks) / 60.0
    mistakes = arr(comp)[comp != 0]
    mistakeTs = arr(times)[comp != 0]
    for c, t in zip(mistakes, mistakeTs):
        log(f'found a possible mis-detect of {c} at {t}')
    log(f'{len(mistakes)=}')
    l = PlotData(
        item_type='line',
        y=comp,
        x=times,
        ylabel='change (ms)',
        title=f'{s1.alg.name()} -> {s2.alg.name()}'
    )
    start = PlotData(
        item_type='line',
        y=[min(comp), max(comp)],
        x=s1.samplesToMins([s1.RAND_SLICE.start, s1.RAND_SLICE.start]),
        item_color='b',
    )
    stop = PlotData(
        item_type='line',
        y=[min(comp), max(comp)],
        x=s1.samplesToMins([s1.RAND_SLICE.stop, s1.RAND_SLICE.stop]),
        item_color='b',
    )
    t = MultiPlot(l, start, stop)
    return t
