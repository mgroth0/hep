from mlib.boot.mlog import log
from qrsalg.PeakDetectionAlg import HEPLAB_Alg
from mlib.boot.mutil import arr, Progress, mymax

class ecglab_fast(HEPLAB_Alg):
    @classmethod
    def versions(cls):
        return {
            1  : 'init',
            2.0: 'artifact catching',
            2.1: 'lookBack',
            2.2: 'plfilt flt2',
            3.0: 'SQUID accepter',
            3.1: 'area adjustment',
            4.0: 'safe_lmt adjustment'
            # ,
            # 3: 'dif_thresh'
            # 2.3: 'adjust plflt for flt2'
            # 'fixPeaks'
            # 'findpeaks of plfilt instead'
        }
    def rpeak_detect(self, ecg_raw, Fs, ecg_flt):
        log('R wave detection in progress... Please wait...')

        log('start fast algorithm')
        # area to look for r events
        area = round(0.070 * Fs)
        # area = round(0.1 * Fs)

        # dif_thresh_gain = 1
        # dif_thresh = None

        # gain
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
        Rwave = []
        qrs = []

        safe_lmt = 0.0

        log('repeat for every cardiac cycle')

        with Progress(sz) as prog:
            while n + 1 < sz:
                if self.version >= 2.1:
                    comp_area = ecg_flt[max(0, n - comp):min(n + comp, sz)]
                    local_comp_area = ecg_flt[max(0, n - local_comp):min(n + local_comp, sz)]
                else:
                    if (n + comp) < sz:
                        comp_area = ecg_flt[n:n + comp]
                    else:
                        comp_area = ecg_flt[(sz - comp) - 1:sz]

                lmt = gain * max(abs(comp_area))
                local_lmt = gain * max(abs(local_comp_area))

                if self.version >= 2.0:
                    if lmt > 1.5 * safe_lmt and safe_lmt != 0.0:
                        # log(f'caught an art?n={n}/{sz}')
                        lmt = safe_lmt
                        if self.version >= 4:
                            safe_lmt = safe_lmt * 1.001
                    else:
                        safe_lmt = lmt

                if local_lmt > 2 * lmt:
                    lmt = local_lmt

                if (ecg_flt[n] > lmt) and (n + 1 < sz):
                    Rwave.append(n)
                    n = n + step
                else:
                    n = n + step_10ms

                prog.tick(n)

        log('Locate R wave')
        # initiate vars
        # n = 1
        mark_count = len(Rwave)

        # DEBUG
        # self.ecg_flt2 = bandstop(ecg_raw, 59, 61, Fs, 1)

        log('return to signal')
        Rwave = arr(Rwave) - ret
        if Rwave[0] < 1: Rwave[0] = 1

        log('locate R peaks')
        with Progress(mark_count - 2) as prog:
            for i in range(1, mark_count - 1):
                # flag = True

                # while flag:

                MINUS_AREA = 8  # area

                if sz >= (Rwave[i] + area) + 1:
                    _, mark = mymax(abs(self.ecg_flt2[Rwave[i] - MINUS_AREA:Rwave[i] + area]))
                else:
                    _, mark = mymax(abs(self.ecg_flt2[Rwave[i] - MINUS_AREA:sz]))
                    # if self.version < 3:
                    #     flag = False
                    # else:

                mark = mark - MINUS_AREA

                # calculate and save mark
                mark = mark + Rwave[i]  # -1

                # DEBUG
                # if (mark / 2000.0) > (9.3175 * 60):
                # peak 246(pyi=245)
                #     self.ecg_flt2[mark]

                # WHY (DEBUG)
                # mark = mark - 100


                qrs.append(mark)

                prog.tick()

        if not list(Rwave):
            qrs = -1

        # if self.version >= 1.1:
        #     qrs = self.fixpeaks(qrs, self.ecg_flt2, AUTO=True)

        log('returning qrs')
        return qrs
