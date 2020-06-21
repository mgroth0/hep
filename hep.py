from mlib.FigData import makefig
from HEP_lib import compare_IBI
from HEP_Params import SUBJECTS, PLOT_FILE, SAVE
from mlib.web.makereport_lib import DOCS_FOLDER
from mlib.web.web import HTMLPage, AutoHTMLImage, HTMLIndex
figs = [[plot] for s in SUBJECTS for plot in s.plots()]
figs += [[compare_IBI(SUBJECTS[0], SUBJECTS[1])]]
makefig(figs, file=PLOT_FILE, show=False)
HTMLIndex(
    HTMLPage(
        'main',
        AutoHTMLImage(PLOT_FILE.rel_to(DOCS_FOLDER)),
    ),
    HTMLPage(
        'test1/test2',
        AutoHTMLImage(PLOT_FILE.rel_to(DOCS_FOLDER)),
    )
).write().open()
if SAVE: [s.savepeaks() for s in SUBJECTS]
