from math import inf

from HEP_lib import compare_IBI, HEP_Subject
from mlib.web.shadow import Shadow
from qrsalg import ManualPeakDetection, ECGLAB_Original

project.init() # placeholder since I don't want project code always executed

shadow = Shadow(show=True)

# DOC: Link: bilinear,https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.bilinear.html

SUBJECTS = [
    HEP_Subject(
        'EP1163',
        [
            'TEN_SECOND_PILOT'
            # 'TEN_MINUTE_TEST'
            # 'FULL'
        ][0], [
            (ManualPeakDetection, inf, 'CALC'),
            (ECGLAB_Original, inf, 'CALC'),
            # (ecglab_fast, inf, 'CALC'),
            # (ecglab_slow, inf, 'CALC'),
            # (pan_tompkins, inf, 'CALC'),
        ][x],
        (6, 2)  # (555,562)
    ) for x in range(2)
]

shadow.fig(
    [[plot] for s in SUBJECTS for plot in s.plots()] + [[compare_IBI(SUBJECTS[0], SUBJECTS[1])]]
)

if False: [s.savepeaks() for s in SUBJECTS]
