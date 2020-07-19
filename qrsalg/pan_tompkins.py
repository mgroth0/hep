# https://github.com/c-labpl/qrs_detector
# started there, then got help from a matlab alg, wikipedia, and
# https://github.com/berndporr/py-ecg-detectors/blob/master/ecgdetectors.py

from qrsalg.PeakDetectionAlg import PeakDetectionAlg

class pan_tompkins(PeakDetectionAlg):

    # Configuration parameters.
    FILTER_LOWCUT = 5.0
    FILTER_HIGHCUT = 15.0
    FILTER_ORDER = 1

    FINDPEAKS_LIMIT = 0.35

    '''Fs factors must be multiplied by Fs'''
    # Fs was originally 250
    FINDPEAKS_SPACING_FS_FACTOR = 1 / 5
    INTEGRATION_WINDOW_FS_FACTOR = 3 / 50
    REFRACTORY_PERIOD_FS_FACTOR = 1 / 4

    QRS_PEAK_FILTERING_FACTOR = 0.125
    NOISE_PEAK_FILTERING_FACTOR = 0.125
    QRS_NOISE_DIFF_WEIGHT = 0.25

    def __init__(self):
        # Measured and calculated values.
        self.filtered_ecg_measurements = None
        self.differentiated_ecg_measurements = None
        self.squared_ecg_measurements = None
        self.integrated_ecg_measurements = None
        self.detected_peaks_indices = None
        self.detected_peaks_values = None

        self.qrs_peak_value = 0.0
        self.noise_peak_value = 0.0
        self.threshold_value = 0.0

        # Detection results.
        self.qrs_peaks_indices = np.array([], dtype=int)
        self.noise_peaks_indices = np.array([], dtype=int)

    def preprocess(self, ecg, Fs):
        log('Measurements filtering - 0-15 Hz band pass filter')
        self.filtered_ecg_measurements = self.bandpass_filter(
            ecg,
            lowcut=self.FILTER_LOWCUT,
            highcut=self.FILTER_HIGHCUT,
            signal_freq=Fs,
            filter_order=self.FILTER_ORDER
        )

        self.filtered_ecg_measurements[:5] = self.filtered_ecg_measurements[5]

        log('Derivative - provides QRS slope information.')
        self.differentiated_ecg_measurements = np.ediff1d(self.filtered_ecg_measurements)

        log('Squaring - intensifies values received in derivative.')
        self.squared_ecg_measurements = self.differentiated_ecg_measurements ** 2

        log('Moving-window integration.')
        integrated_ecg_measurements = np.convolve(self.squared_ecg_measurements,
                                                  np.ones(assert_int(self.INTEGRATION_WINDOW_FS_FACTOR * Fs)))

        return integrated_ecg_measurements

    def rpeak_detect(self, ecg_raw, Fs, ecg_flt, ecg_raw_nopl_high):
        log('Run whole detector flow.')
        log('Fiducial mark - peak detection on integrated measurements.')
        self.detected_peaks_indices = self.findpeaks(data=ecg_flt,
                                                     # limit=self.FINDPEAKS_LIMIT,
        #Matt: I am sure that findpeaks_limit is some weird number invented by the guy who wrote this python implementation. I didn't see any reference to it in a matlab implementation nor the wikipedia summary, and the sample data for the python implementation had ecg data that was in the range of like 0 to 2 whereas mine is hundreds
                                                     limit=None,
                                                     spacing=self.FINDPEAKS_SPACING_FS_FACTOR * Fs)

        self.detected_peaks_values = ecg_flt[self.detected_peaks_indices]
        log('detecting qrs')
        self.detect_qrs(ecg_flt, Fs)
        log('returning qrs')
        return self.qrs_peaks_indices

    """ECG measurements data processing methods."""

    """QRS detection methods."""

    def detect_qrs(self, ecg_flt, Fs):
        """
        Method responsible for classifying detected ECG measurements peaks either as noise or as QRS complex (heart beat).
        """
        sz = len(self.detected_peaks_indices)

        RR_missed = 0
        signal_peaks = [0]
        noise_peaks = []
        index = -1
        prog = Progress(sz)
        for detected_peak_index, detected_peaks_value in zip(self.detected_peaks_indices, self.detected_peaks_values):
            index = index + 1
            if index==0 or index == len(self.detected_peaks_indices)-1:
                prog.tick()
                continue
            try:
                last_qrs_index = self.qrs_peaks_indices[-1]
            except IndexError:
                last_qrs_index = 0

            # After a valid QRS complex detection, there is a 200 ms refractory period before next one can be detected.
            if detected_peak_index - last_qrs_index > (
                    self.REFRACTORY_PERIOD_FS_FACTOR * Fs) or not self.qrs_peaks_indices.size:
                # Peak must be classified either as a noise peak or a QRS peak.
                # To be classified as a QRS peak it must exceed dynamically set threshold value.


                if detected_peaks_value > self.threshold_value:
                    self.qrs_peaks_indices = np.append(self.qrs_peaks_indices, detected_peak_index)

                    # Adjust QRS peak value used later for setting QRS-noise threshold.
                    self.qrs_peak_value = self.QRS_PEAK_FILTERING_FACTOR * detected_peaks_value + \
                                          (1 - self.QRS_PEAK_FILTERING_FACTOR) * self.qrs_peak_value
                else:
                    self.noise_peaks_indices = np.append(self.noise_peaks_indices, detected_peak_index)

                    # Adjust noise peak value used later for setting QRS-noise threshold.
                    self.noise_peak_value = self.NOISE_PEAK_FILTERING_FACTOR * detected_peaks_value + \
                                            (1 - self.NOISE_PEAK_FILTERING_FACTOR) * self.noise_peak_value

                # Adjust QRS-noise threshold value based on previously detected QRS or noise peaks value.
                self.threshold_value = self.noise_peak_value + \
                                       self.QRS_NOISE_DIFF_WEIGHT * (self.qrs_peak_value - self.noise_peak_value)
                prog.tick()

    """Tools methods."""

    def bandpass_filter(self, data,
                        lowcut,
                        highcut, signal_freq, filter_order):
        """
        Method responsible for creating and applying Butterworth filter.
        :param deque data: raw data
        :param float lowcut: filter lowcut frequency value
        :param float highcut: filter highcut frequency value
        :param int signal_freq: signal frequency in samples per second (Hz)
        :param int filter_order: filter order
        :return array: filtered data
        """
        nyquist_freq = 0.5 * signal_freq
        low = lowcut / nyquist_freq
        high = highcut / nyquist_freq
        b, a = butter(filter_order, (low,high), btype="bandpass")
        # b, a = butter(filter_order, high, btype="lowpass")
        y = lfilter(b, a, data)
        return y

    def findpeaks(self, data, spacing=1, limit=None):
        """
        Janko Slavic peak detection algorithm and implementation.
        https://github.com/jankoslavic/py-tools/tree/master/findpeaks
        Finds peaks in `data` which are of `spacing` width and >=`limit`.
        :param ndarray data: data
        :param float spacing: minimum spacing to the next peak (should be 1 or more)
        :param float limit: peaks should have value greater or equal
        :return array: detected peaks indexes array
        """
        length = data.size
        spacing = assert_int(spacing)
        x = np.zeros(length + 2 * spacing)
        x[:spacing] = data[0] - 1.e-6
        x[-spacing:] = data[-1] - 1.e-6
        x[spacing:spacing + length] = data
        peak_candidate = np.zeros(length)
        peak_candidate[:] = True
        prog = Progress(spacing)
        for s in range(spacing):
            start = spacing - s - 1
            h_b = x[start: start + length]  # before
            start = spacing
            h_c = x[start: start + length]  # central
            start = spacing + s + 1
            h_a = x[start: start + length]  # after
            peak_candidate = np.logical_and(peak_candidate, np.logical_and(h_c > h_b, h_c > h_a))
            prog.tick()

        ind = np.argwhere(peak_candidate)
        ind = ind.reshape(ind.size)
        if limit is not None:
            ind = ind[data[ind] > limit]
        return ind
