from numpy import double, diff
import numpy as np

from mlib.boot.mlog import log
from mlib.boot.mutil import assert_int, SyncedDataFolder, arr, File, isinstsafe, itr, nopl
from qrsalg.PeakDetectionAlg import HEPLAB_Alg
from qrsalg import ManualPeakDetection

from mlib.FigData import Line, Scat, addToCurrentFigSet, MultiPlot
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
    def __init__(self, sub_id, dataset, alg):
        self.id = sub_id
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
        self.raw = None
        self.ecg = None
        self.Fs = None
        self.ecg_flt = None
        self.ecg_nopl = None
        self.rPeaks = None
    def get_Fs(self):
        if self.Fs is None:
            self.load()
        return self.Fs
    def loadpeaks(self):
        # temp
        # self.peakfile = HEP_Data(self.peakfile.name.replace('.mat','_manual.mat'))

        # if isinstance(self.alg,ManualPeakDetection):
        #     self.rPeaks = self.peakfile['manual_'+str(self.alg.version)]['py'][0][0].flatten()
        # else:

        self.rPeaks = self.peakfile[self.alg.name()]['py'][0][0].flatten()


        self.rPeaks = self.rPeaks[self.rPeaks >= self.rawslice.start]
        self.rPeaks = self.rPeaks[self.rPeaks < self.rawslice.stop]

        # TEMP, removing first and last of manual to match others
        # self.rPeaks =self.rPeaks[1:-1]


        assert len(self.rPeaks.shape) == 1
        assert len(self.rPeaks) > 2
        # if self.alg.__class__.__name__ == 'ManualPeakDetection' and self.alg.version >= 1.1:
        #     self.preprocess()
        #     self.rPeaks = self.alg.fixpeaks(self.rPeaks,self.ecg_flt,AUTO=True)
        #
        # # temp
        # self.peakfile = HEP_Data(self.peakfile.name.replace('_manual.mat','.mat'))

        return self.rPeaks
    def load(self):
        if self.raw is None:
            self.raw = self.rawfile.load()
            self.Fs = self.raw.Fs
        return self.raw
    def __getitem__(self, item):
        if self.raw is None: self.load()
        self.ecg = self.raw[self.raw.ECG_CHAN, item]
        return self.ecg

    def times(self, indices=None):
        if indices is None: indices = self.rawslice
        if not isinstance(indices, slice):
            if len(indices) == 0: return arr()
            t = self.load().times(slice(
                min(indices),
                max(indices) + 1))
            indices = arr(indices) - min(indices)
            t = t[indices]
        else:
            t = self.load().times(indices)
        return t

    def preprocess(self):
        if self.ecg is None:
            # noinspection PyStatementEffect
            self[self.rawslice]
        self.ecg_flt = self.alg.preprocess(self.ecg, self.raw.Fs)
        return self.ecg_flt
    def nopl(self):
        if self.ecg is None:
            # noinspection PyStatementEffect
            self[self.rawslice]
        self.ecg_nopl = nopl(self.ecg, self.Fs)
        return self.ecg_nopl
    def rpeak_detect(self):

        # ugly coding, but its needed for Manual
        self.alg.rawslice = self.rawslice

        if self.ecg_flt is None:
            self.preprocess()
        self.rPeaks = arr(self.alg.rpeak_detect(self.ecg, self.Fs, self.ecg_flt))
        return self.rPeaks
    def rpeak_get(self):
        if self.rPeaks is None:
            if self.algmode == 'LOAD':
                self.loadpeaks()
            else:
                self.rpeak_detect()

        # self.rPeaks = arr(self.rPeaks)[
        #     np.bitwise_and(self.rPeaks >= 10 * self.Fs, self.rPeaks < len(self.times()) - 10 * self.Fs)]
        #
        return self.rPeaks

    def plot_example_rpeaks(self):
        import HEP_Params
        l = Line(
            y=self.preprocess(),
            x=self.times() / 60.0,
            xlim=self.samplesToMins(HEP_Params.RAND_SLICE),
            xlabel='time (mins)',
            ylim='auto', add=False,
            hideYTicks=True
        )
        s = Scat(
            y=self.preprocess()[self.rpeak_get()],
            x=self.samplesToMins(self.rpeak_get()),
            item_color='b',
            xlim=self.samplesToMins(HEP_Params.RAND_SLICE),

            title=self.alg.name() + ': example R peaks',
            add=False)
        plots = (l, s)
        if isinstsafe(self.alg, HEPLAB_Alg):
            l2 = Line(
                y=self.alg.ecg_flt2,
                x=self.times() / 60.0,
                xlim=self.samplesToMins(HEP_Params.RAND_SLICE),
                xlabel='time (mins)',
                ylim='auto',
                item_color='g',
                add=False)
            plots = tuple(list(plots) + [l2])
        t = MultiPlot(*plots)
        addToCurrentFigSet(t)
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
        import HEP_Params
        ibi = self.samplesToMs(diff(self.rpeak_get()))
        l = Line(
            y=ibi,
            x=self.times(self.rPeaks[1:]) / 60.0,
            title=self.alg.name() + ': IBIs',
            ylabel='IBI (ms)',
            xlabel='time (mins)',
            add=False
        )
        start = Line(
            y=[min(ibi, default=0), max(ibi, default=1)],
            x=self.samplesToMins([HEP_Params.RAND_SLICE.start, HEP_Params.RAND_SLICE.start]),
            item_color='b',
        )
        stop = Line(
            y=[min(ibi, default=0), max(ibi, default=1)],
            x=self.samplesToMins([HEP_Params.RAND_SLICE.stop, HEP_Params.RAND_SLICE.stop]),
            item_color='b',
        )
        t = MultiPlot(l, start, stop)
        addToCurrentFigSet(t)
        return t


    def savepeaks(self):
        if self.algmode == 'LOAD':
            log('skipping savepeaks for ' + str(self) + ' because data was loaded from file')
            #
            return False

        if self.rPeaks is None:
            self.rpeak_get()

        # obsolete stuff
        # if 'heartbeatevents_py' in self.peakfile.load().keys():
        #     del self.peakfile['heartbeatevents_py']
        #     del self.peakfile['heartbeatevents_mat']

        export = {
            'latency': arr(self.rPeaks) + 1,
            'type'   : ['ECG' for i in itr(self.rPeaks)],
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
        ar = np.ndarray(shape=(2, 1), dtype=MultiPlot)
        ar[:, :] = [
            [self.plot_example_rpeaks()],
            [self.plot_IBIs()]
        ]
        return ar

def compare_IBI(s1, s2):
    import HEP_Params
    comp = s1.samplesToMs(s2.rpeak_get() - s1.rpeak_get())
    times = s1.times(s1.rPeaks) / 60.0
    mistakes = arr(comp)[comp != 0]
    mistakeTs = arr(times)[comp != 0]
    for c, t in zip(mistakes, mistakeTs):
        log(f'found a possible mis-detect of {c} at {t}')
    log(f'{len(mistakes)=}')
    l = Line(
        y=comp,
        x=times,
        ylabel='change (ms)',
        title=f'{s1.alg.name()} -> {s2.alg.name()}',
        add=False
    )
    start = Line(
        y=[min(comp), max(comp)],
        x=s1.samplesToMins([HEP_Params.RAND_SLICE.start, HEP_Params.RAND_SLICE.start]),
        item_color='b',
    )
    stop = Line(
        y=[min(comp), max(comp)],
        x=s1.samplesToMins([HEP_Params.RAND_SLICE.stop, HEP_Params.RAND_SLICE.stop]),
        item_color='b',
    )
    t = MultiPlot(l, start, stop)
    addToCurrentFigSet(t)
    return t
