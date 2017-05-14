import logging
from subprocess import Popen, PIPE

from envirophat import weather

logging.basicConfig()

class TempReader(object):

    def __init__(self, sensor_temp_offset=0):
        self._sensor_temp_offset = sensor_temp_offset
        self.logger = logging.getLogger("temp_reader")
        self.logger.setLevel(logging.INFO)

    def _convert_to_fahrenheit(self, temp_in_celcius):
        return temp_in_celcius * 9.0 / 5.0 + 32.0

    def cpu_temp(self):
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
        output, _error = process.communicate()
        temp = float(output[output.index('=') + 1:output.rindex("'")])
        return self._convert_to_fahrenheit(temp)

    def sensor_temp(self):
        sensor_temp = weather.temperature() + self._sensor_temp_offset
        return self._convert_to_fahrenheit(sensor_temp)

