from mlib.FigData import makefig
from HEP_lib import compare_IBI
from HEP_Params import SUBJECTS, PLOT_FILE, SAVE, figs_folder
from mlib.web.makereport_lib import upload_wolf_webpage, RESOURCES_ROOT
from mlib.web.web import HTML, HTMLImage
from mlib.wolf.wolfpy import WOLFRAM
figs = [[plot] for s in SUBJECTS for plot in s.plots()]
figs += [[compare_IBI(SUBJECTS[0], SUBJECTS[1])]]
makefig(figs, file=PLOT_FILE, show=False)
with WOLFRAM:
    upload_wolf_webpage(
        HTML(
            # HTMLImage(RESOURCES_ROOT + 'hep/' + PLOT_FILE)
            HTMLImage(RESOURCES_ROOT + 'hep/_plot.png')
        ),
        wolfFolder='hep',
        permissions='Public',
        resource_folder=figs_folder
    )
if SAVE: [s.savepeaks() for s in SUBJECTS]
