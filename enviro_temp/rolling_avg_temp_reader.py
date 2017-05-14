from enviro_temp.temp_reader import TempReader
from enviro_temp.utils import RollingAverage


class RollingAvgTempReader(TempReader):

    def __init__(self, rolling_avg_window=10, sensor_temp_offset=0):
        super(RollingAvgTempReader, self).__init__(sensor_temp_offset=sensor_temp_offset)
        self.cpu_temp_queue = RollingAverage(rolling_avg_window)
        self.raw_sensor_temp_queue = RollingAverage(rolling_avg_window)

    def cpu_temp(self):
        temp = super(RollingAvgTempReader, self).cpu_temp()
        self.cpu_temp_queue.add_val(temp)
        return temp

    def sensor_temp(self):
        fahrenheit = super(RollingAvgTempReader, self).sensor_temp()
        self.raw_sensor_temp_queue.add_val(fahrenheit)
        return fahrenheit

    def avg_cpu_temp(self):
        return self.cpu_temp_queue.get_average()

    def avg_sensor_temp(self):
        return self.raw_sensor_temp_queue.get_average(offset=self._sensor_temp_offset)
