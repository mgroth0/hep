from mlib.boot.mutil import arr, Progress, mymax, vers, log_invokation, log
from qrsalg.ECGLAB_QRS_Mod import ECGLAB_QRS_Mod

# TODO: "original" is the goal, but currently its just HEPLAB_fast
class ECGLAB_Original(ECGLAB_QRS_Mod):
    @classmethod
    def versions(cls):
        return {
            '1'  : 'init',
            '2.0': 'artifact catching',
            '2.1': 'lookBack',
            '2.2': 'plfilt flt2',
            '3.0': 'SQUID accepter',
            '3.1': 'area adjustment',
            '4.0': 'safe_lmt adjustment',
            '4.1': 'remove 1 sec trimming',
            '4.2': 'remove heartbeat1 index check'
        }

    @log_invokation()
    def rpeak_detect(self, ecg_raw, Fs, ecg_flt, ecg_raw_nopl_high):
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

        with Progress(sz, 'scanning', 'samples') as prog:
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

        log('return to signal')
        Rwave = arr(Rwave) - ret
        # assert Rwave[0] >= 1
        # if Rwave[0] < 1: Rwave[0] = 1

        log('locate R peaks')
        # TODO: Should merge with fixPeaks()
        with Progress(mark_count, 'searching back on', 'marks') as prog:
            for i in range(mark_count):
                # flag = True

                # while flag:

                MINUS_AREA = min(8, Rwave[i])  # area
                if sz >= (Rwave[i] + area) + 1:
                    _, mark = mymax(abs(ecg_raw_nopl_high[Rwave[i] - MINUS_AREA:Rwave[i] + area]))
                else:
                    _, mark = mymax(abs(ecg_raw_nopl_high[Rwave[i] - MINUS_AREA:sz]))
                    # if self.version < 3:
                    #     flag = False
                    # else:

                mark = mark - MINUS_AREA

                # calculate and save mark
                mark = mark + Rwave[i]  # -1

                qrs.append(mark)

                prog.tick()

        assert list(Rwave)
        if not list(Rwave):
            qrs = -1
        return qrs
