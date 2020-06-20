# import HEP_Main

from mlib.FigData import makefig
from HEP_lib import *
import HEP_Params
from HEP_Params import *


def compare_IBI(s1, s2):
    comp = s1.samplesToMs(s2.rpeak_get() - s1.rpeak_get())
    times = s1.times(s1.rPeaks) / 60.0
    mistakes = arr(comp)[comp!=0]
    mistakeTs = arr(times)[comp!=0]
    for c,t in zip(mistakes,mistakeTs):
        log(f'found a possible mis-detect of {c} at {t}')
    log(f'mistake count: {len(mistakes)}')
    l = Line(
        y=comp,
        x=times,
        ylabel='change (ms)',
        title=s1.alg.name() + ' -> ' + s2.alg.name(),
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

def main(s):
    # diff the qrs of each
    ar = np.ndarray(shape=(2, 1), dtype=MultiPlot)
    ar[:, :] = [
        [s.plot_example_rpeaks()],
        [s.plot_IBIs()]
    ]
    return ar
if __name__ == '__main__':
    # HEP_DATA_FOLDER.presync()
    mains = tuple([main(s) for s in SUBJECTS])
    mains = np.vstack(mains)


    figs = mains


    # ar = np.ndarray(shape=(1, 1), dtype=MultiPlot)
    # comp = [[compare_IBI(SUBJECTS[0], SUBJECTS[1])]]
    # ar[:, :] = comp
    # figs = np.vstack((mains, ar))
    # figs = tuple(figs)
    # figs = np.vstack(figs)


    makefig(figs,plotarg = PLOT)
    # if SAVE and any([s.savepeaks() for s in SUBJECTS]):
        # HEP_DATA_FOLDER.postsync()
    import os
    log('HEP code finished without error. Exiting')
    os._exit(0)
