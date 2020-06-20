from mlib.FigData import makefig
from HEP_lib import compare_IBI
from HEP_Params import SUBJECTS, PLOT_FILE, SAVE
from mlib.web.makereport_lib import RESOURCES_ROOT, prep_gitlfs_webpage
from mlib.web.web import HTML, HTMLImage
from mlib.wolf.wolfpy import WOLFRAM
figs = [[plot] for s in SUBJECTS for plot in s.plots()]
figs += [[compare_IBI(SUBJECTS[0], SUBJECTS[1])]]
makefig(figs, file=PLOT_FILE, show=False)
DOCS_ROOT = 'https://mgroth0.github.io/hep/'
with WOLFRAM:
    prep_gitlfs_webpage(
        HTML(
            HTMLImage(f'{DOCS_ROOT}resources/figs/plot.png')
        ),
    )
if SAVE: [s.savepeaks() for s in SUBJECTS]
