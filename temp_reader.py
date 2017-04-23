import threading
import time
from subprocess import Popen, PIPE

from utils import RollingAverage


class TempReader(object):

    def __init__(self):
        self.cpu_temp_queue = RollingAverage(10)
        self._last_cpu_temp_reading = None
        self._last_sensor_temp_reading = None

    def _add_cpu_temp_to_queue(self, val=None):
        if not val:
            val = self.instant_cpu_temp()
        print "Adding CPU temp to queue {}".format(val)
        self.cpu_temp_queue.add_val(val)

    def _convert_to_fahrenheit(self, temp_in_celcius):
        return temp_in_celcius * 9.0 / 5.0 + 32.0

    def avg_cpu_temp(self):
        return self.cpu_temp_queue.get_average()

    def instant_cpu_temp(self):
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
        output, _error = process.communicate()
        temp = float(output[output.index('=') + 1:output.rindex("'")])
        temp = self._convert_to_fahrenheit(temp)
        self._last_cpu_temp_reading = temp
        return temp

    # No need for an avg sensor temp because the signal is clean already

    def instant_sensor_temp(self):
        sensor_temp = weather.temperature()
        self._last_sensor_temp_reading = sensor_temp
        return self._convert_to_fahrenheit(sensor_temp)


class CalibratedTempReader(TempReader):

    def __init__(self, calibration_factor):
        super(CalibratedTempReader, self).__init__()
        self.calibration_factor = calibration_factor
        self._thread_fill_frequency = 1 # Hz
        self.calibrated_queue = RollingAverage(5)
        self._queue_filler_thread = threading.Thread(target=self._queue_filler_thread_func)
        self._stop_thread = False
        self._start_filling_queue()

    def _calibrate_temp(self, sensor_temp, cpu_temp):
        calibrated_temp = sensor_temp - ((cpu_temp - sensor_temp) / self.calibration_factor)
        return calibrated_temp

    def _read_and_add_calibrated_temp_to_queue(self):
        val = self.instant_calibrated_temp()
        print "Adding calibrated temp to queue {}".format(val)
        self.calibrated_queue.add_val(val)
        # We just did a read of CPU temp to get the above val so lets drop it in our queue
        self._add_cpu_temp_to_queue(self._last_cpu_temp_reading)

    def _queue_filler_thread_func(self):
        while not self._stop_thread:
            print "Thread loop"
            self._read_and_add_calibrated_temp_to_queue()
            time.sleep(self._thread_fill_frequency)

    def _start_filling_queue(self):
        self._stop_thread = False
        self._queue_filler_thread.start()
        while not self.calibrated_queue.is_full:
            print "Waiting for queue to fill up... (currently: {})".format(self.calibrated_queue.values)
            time.sleep(1)
        return True

    def stop_thread(self):
        print "Stopping queue filler thread"
        self._stop_thread = True
        self._queue_filler_thread.join()

    def avg_calibrated_temp(self):
        return self.calibrated_queue.get_average()

    def instant_calibrated_temp(self):
        sensor_temp = self.instant_sensor_temp()
        cpu_temp = self.instant_cpu_temp()
        return self._calibrate_temp(sensor_temp, cpu_temp)