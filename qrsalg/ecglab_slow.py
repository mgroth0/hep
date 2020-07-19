from numpy import fix, mean, ones

from mlib.boot.mlog import log
from mlib.boot.stream import mymax
from mlib.err import assert_int
from mlib.term import Progress
from qrsalg.ECGLAB_QRS_Mod import ECGLAB_QRS_Mod

class ecglab_slow(ECGLAB_QRS_Mod):

    def rpeak_detect(self, ecg_raw, Fs, ecg_flt, ecg_raw_nopl_high):
        ecg = self.ecg_raw  # only needed for ecglab_slow

        log('R wave detection in progress... Please wait...')

        log('start slow algorithm')
        # find peak
        step = round(0.200 * Fs)
        area = 2 * Fs
        ret = assert_int(0.160 * Fs)

        sz = len(ecg_flt)
        ecg_temp = -1500 * ones((sz, 1))
        n = 0
        qrs = []

        log('repeat for every cardiac cycle')

        prog = Progress(sz)

        while n + 1 < sz:
            prog.tick(n)

            maxval = 0
            ind = None

            if (n + area) < sz:
                lm = 0.15 * max(abs(ecg_flt[n:n + area]))
            else:
                lm = 0.15 * max(abs(ecg_flt[(sz - area) - 1:sz]))

            while (ecg_flt[n] > lm) and (n + 1 < sz):
                if abs(ecg_flt[n]) > maxval:
                    maxval = abs(ecg_flt[n])
                    ind = n
                n = n + 1

            if ind is not None:
                ecg_temp[ind] = 1
                n = ind + step
            else:
                n = n + 1

        for kk in range(0, sz - Fs, Fs):
            ecg[kk:kk + Fs - 1] = ecg[kk:kk + Fs - 1] - mean(ecg[kk:kk + Fs - 1])

        d1 = ret
        n = 0

        prog = Progress(sz)

        while n + 1 <= sz:
            prog.tick(n)

            maxval = 0
            ind = None
            while ecg_temp[n] == 1 and n + 1 <= sz:
                if (n + 1) - d1 > 0:
                    ini = n - ret
                else:
                    ini = 0

                maxval, ind = mymax(abs(ecg[ini:n + 1]))
                ind = fix(ini + ind)
                qrs.append(ind)
                n += 1
            n += 1
        if len(qrs) == 0:
            qrs = -1

        log('returning qrs')
        return qrs
