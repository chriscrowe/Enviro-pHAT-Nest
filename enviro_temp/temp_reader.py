import logging
import signal
import threading
import time
from subprocess import Popen, PIPE

from envirophat import weather

from utils import RollingAverage

logging.basicConfig()

class TempReader(object):

    def __init__(self, rolling_avg_window=10):
        self.cpu_temp_queue = RollingAverage(rolling_avg_window)
        self.raw_sensor_temp_queue = RollingAverage(rolling_avg_window)
        self._last_cpu_temp_reading = None
        self.logger = logging.getLogger("temp_reader")
        self.logger.setLevel(logging.INFO)

    def _convert_to_fahrenheit(self, temp_in_celcius):
        return temp_in_celcius * 9.0 / 5.0 + 32.0

    def cpu_temp(self):
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
        output, _error = process.communicate()
        temp = float(output[output.index('=') + 1:output.rindex("'")])
        temp = self._convert_to_fahrenheit(temp)
        self.cpu_temp_queue.add_val(temp)
        return temp

    def avg_cpu_temp(self):
        return self.cpu_temp_queue.get_average()

    def sensor_temp(self):
        sensor_temp = weather.temperature()
        fahrenheit = self._convert_to_fahrenheit(sensor_temp)
        self.raw_sensor_temp_queue.add_val(fahrenheit)
        return fahrenheit

    def avg_sensor_temp(self):
        return self.raw_sensor_temp_queue.get_average()


class CalibratedTempReader(TempReader):

    def __init__(self, calibration_factor=1.1, rolling_avg_window=15, constant_offset=-10):
        super(CalibratedTempReader, self).__init__(rolling_avg_window=rolling_avg_window)
        self.calibration_factor = calibration_factor
        self._constant_offset = constant_offset
        self._thread_fill_frequency = 1 # Hz
        self.calibrated_queue = RollingAverage(rolling_avg_window)
        self._queue_filler_thread = threading.Thread(target=self._queue_filler_thread_func)
        self._stop_thread = False
        signal.signal(signal.SIGINT, self.stop_thread)
        self._start_filling_queue()

    def is_running(self):
        return not self._stop_thread

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

    def stop_thread(self, *args, **kwargs):
        self.logger.debug("Stopping queue filler thread")
        self._stop_thread = True
        self._queue_filler_thread.join()

    def calibrated_temp(self):
        sensor_temp = self.sensor_temp()
        cpu_temp = self.cpu_temp()
        return self._calibrate_temp(sensor_temp, cpu_temp)

    def offset_temp(self):
        return self.sensor_temp() + self._constant_offset

    # instant_sensor_temp is in super class

    def avg_calibrated_temp(self):
        return self.calibrated_queue.get_average()

    def avg_offset_temp(self):
        return self.raw_sensor_temp_queue.get_average(offset=self._constant_offset)

    # avg_instant_sensor_temp is in super class
