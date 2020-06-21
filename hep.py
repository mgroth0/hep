from mlib.FigData import makefig
from HEP_lib import compare_IBI
from HEP_Params import SUBJECTS, PLOT_FILE, SAVE
from mlib.web.makereport_lib import DOCS_FOLDER
from mlib.web.web import HTMLPage, AutoHTMLImage, HTMLIndex
from qrsalg import ECGLAB_QRS_Mod
figs = [[plot] for s in SUBJECTS for plot in s.plots()]
figs += [[compare_IBI(SUBJECTS[0], SUBJECTS[1])]]
makefig(figs, file=PLOT_FILE, show=False)
HTMLIndex(
    HTMLPage(
        'main',
        AutoHTMLImage(PLOT_FILE.rel_to(DOCS_FOLDER)),
    ),
    ECGLAB_QRS_Mod.DOC
).write().open()
if SAVE: [s.savepeaks() for s in SUBJECTS]
