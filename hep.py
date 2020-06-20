from mlib.FigData import makefig
from HEP_lib import compare_IBI
from HEP_Params import SUBJECTS, PLOT_FILE, SAVE
from mlib.boot.mutil import Folder
from mlib.web.web import HTML, HTMLImage
from mlib.wolf.wolfpy import WOLFRAM
figs = [[plot] for s in SUBJECTS for plot in s.plots()]
figs += [[compare_IBI(SUBJECTS[0], SUBJECTS[1])]]
makefig(figs, file=PLOT_FILE, show=False)
docs = Folder('docs').mkdir()
with WOLFRAM:
    docs['index.html'].write(
        HTML(HTMLImage(
            WOLFRAM.copy_file(PLOT_FILE, f'Resources/HEP/{PLOT_FILE}', permissions="Public")[0]
        )).getCode()
    )
if SAVE: [s.savepeaks() for s in SUBJECTS]
