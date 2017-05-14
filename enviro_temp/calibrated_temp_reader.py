import signal
import threading
import time

from enviro_temp.rolling_avg_temp_reader import RollingAvgTempReader
from enviro_temp.utils import RollingAverage


class CalibratedTempReader(RollingAvgTempReader):

    def __init__(self, calibration_factor=1.1, rolling_avg_window=15):
        super(CalibratedTempReader, self).__init__(rolling_avg_window=rolling_avg_window)
        self.calibration_factor = calibration_factor
        self._thread_fill_frequency = 1 # Hz
        self.calibrated_queue = RollingAverage(rolling_avg_window)
        self._queue_filler_thread = threading.Thread(target=self._queue_filler_thread_func)
        self._stop_thread = False
        signal.signal(signal.SIGINT, self.stop_thread)
        self._start_filling_queue()

    def _calibrate_temp(self, sensor_temp, cpu_temp):
        calibrated_temp = sensor_temp - ((cpu_temp - sensor_temp) / self.calibration_factor)
        return calibrated_temp

    def _read_and_add_calibrated_temp_to_queue(self):
        val = self.calibrated_temp()
        self.logger.info("Adding calibrated temp to queue {}".format(val))
        self.calibrated_queue.add_val(val)

    def _queue_filler_thread_func(self):
        try:
            while not self._stop_thread:
                self.logger.debug("Thread loop")
                self._read_and_add_calibrated_temp_to_queue()
                time.sleep(self._thread_fill_frequency)
        except KeyboardInterrupt:
            return

    def _start_filling_queue(self):
        self._stop_thread = False
        self._queue_filler_thread.start()
        self.logger.info("Waiting for queue of size {} to fill".format(self.calibrated_queue.window_size))
        while not self.calibrated_queue.is_full:
            self.logger.debug("Waiting for queue ({}) to fill up... (currently: {})".format(self.calibrated_queue.window_size, self.calibrated_queue.values))
            time.sleep(1)
        return True

    def is_running(self):
        return not self._stop_thread

    def stop_thread(self, *args, **kwargs):
        self.logger.debug("Stopping queue filler thread")
        self._stop_thread = True
        self._queue_filler_thread.join()

    def calibrated_temp(self):
        sensor_temp = self.sensor_temp()
        cpu_temp = self.cpu_temp()
        return self._calibrate_temp(sensor_temp, cpu_temp)

    def avg_calibrated_temp(self):
        return self.calibrated_queue.get_average()
