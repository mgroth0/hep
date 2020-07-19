from mlib.boot import log
from mlib.boot.stream import arr
from mlib.file import File
from mlib.proj.struct import vers
from mlib.term import log_invokation, Progress
from mlib.web.shadow import Shadow
from qrsalg.ECGLAB_QRS_Mod import ECGLAB_QRS_Mod
from qrsalg.PeakDetectionAlg import find_local_maxima

DOC = Shadow(
    bib='hep_bib.yml'
)

# TODO: "original" is the goal, but currently its just HEPLAB_fast
class ECGLAB_Original(ECGLAB_QRS_Mod):


    # DOC: START

    DOC.H2(
        'R Peak Detection',
        style={'text-align': 'center'}
    )

    @log_invokation
    def rpeak_detect(
            self,
            ecg_raw,
            Fs,
            ecg_flt,
            ecg_raw_nopl_high
    ):
        log('start fast algorithm')
        # area to look for r events
        area = round(0.070 * Fs)

        gain = 0.15

        # comparison limit: 2 sec
        comp = round(2 * Fs)
        local_comp = round(0.2 * Fs)

        # minimum interval between marks (350ms)
        step = round(0.350 * Fs)

        # 10ms step
        step_10ms = round(0.01 * Fs)

        ret = round(0.030 * Fs)

        # initiate vars
        sz = len(ecg_flt)
        n = 0
        r_peak_indices = []

        safe_lmt = 0.0

        log('repeat for every cardiac cycle')

        # DOC: STOP
        with Progress(sz, 'scanning', 'samples') as prog:
            # DOC: START
            while n + 1 < sz:
                if vers(self.version) >= vers(2.1):
                    comp_area = ecg_flt[max(0, n - comp):min(n + comp, sz)]
                    local_comp_area = ecg_flt[max(0, n - local_comp):min(n + local_comp, sz)]
                else:
                    if (n + comp) < sz:
                        comp_area = ecg_flt[n:n + comp]
                    else:
                        comp_area = ecg_flt[(sz - comp) - 1:sz]

                lmt = gain * max(abs(comp_area))
                local_lmt = gain * max(abs(local_comp_area))

                if vers(self.version) >= vers(2.0):
                    if lmt > 1.5 * safe_lmt and safe_lmt != 0.0:
                        # log(f'caught an art?n={n}/{sz}')
                        lmt = safe_lmt
                        if vers(self.version) >= vers(4):
                            safe_lmt *= 1.001
                    else:
                        safe_lmt = lmt

                if local_lmt > 2 * lmt:
                    lmt = local_lmt

                if (ecg_flt[n] > lmt) and (n + 1 < sz):
                    r_peak_indices.append(n)
                    n += step
                else:
                    n += step_10ms

                # DOC: STOP
                prog.tick(n)
                # DOC: START

        log('return to signal')
        r_peak_indices = arr(r_peak_indices) - ret

        return find_local_maxima(
            r_peak_indices,
            ecg_raw_nopl_high,
            FIX_WIDTH=(8, area)
        )


DOC.write_bib()
