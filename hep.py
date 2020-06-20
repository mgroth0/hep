import numpy as np

from HEP_lib import compare_IBI
from mlib.boot.mlog import log
from mlib.FigData import makefig, MultiPlot
from HEP_Params import SUBJECTS, PLOT, SAVE

mains = tuple([s.plots() for s in SUBJECTS])
mains = np.vstack(mains)
figs = mains
ar = np.ndarray(shape=(1, 1), dtype=MultiPlot)
comp = [[compare_IBI(SUBJECTS[0], SUBJECTS[1])]]
ar[:, :] = comp
figs = np.vstack((mains, ar))
figs = tuple(figs)
figs = np.vstack(figs)
makefig(figs, plotarg=PLOT)
if SAVE:
    new_data = any([s.savepeaks() for s in SUBJECTS])
else: new_data=False
log(f'Finished heartbeat analysis!({new_data=})')
