import time

from mlib.FigData import makefig
from HEP_lib import compare_IBI
from HEP_Params import SUBJECTS, PLOT_FILE, SAVE
from mlib.boot.mutil import refreshSafariReport, shell, File
from mlib.web.makereport_lib import prep_webpage, push_docs
from mlib.web.web import HTML, HTMLImage, AutoHTMLImage
figs = [[plot] for s in SUBJECTS for plot in s.plots()]
figs += [[compare_IBI(SUBJECTS[0], SUBJECTS[1])]]
makefig(figs, file=PLOT_FILE, show=False)
DOCS_ROOT = 'https://mgroth0.github.io/hep/'
DOCS_ROOT_OFFLINE_VERSION = File('_docs/index.html').url()
IMAGE_ROOT = 'https://media.githubusercontent.com/media/mgroth0/hep/master/docs/'
prep_webpage(
    HTML(
        AutoHTMLImage(f'resources/figs/plot.png'),
    ),
    web_resources_root=IMAGE_ROOT
)
refreshSafariReport(DOCS_ROOT_OFFLINE_VERSION)
if SAVE: [s.savepeaks() for s in SUBJECTS]
