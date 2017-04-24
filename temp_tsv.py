import logging
import time
from temp_reader import CalibratedTempReader

def main():
    cal_temp_reader = CalibratedTempReader(calibration_factor=1.1, rolling_avg_window=5)
    # cal_temp_reader.logger.setLevel(logging.DEBUG)

    print "Instant CPU\tAvg CPU\tInstant Sensor\tAvg Sensor (Calibrated)"
    while cal_temp_reader.is_running():
        instant_cpu_temp = cal_temp_reader.instant_cpu_temp()
        avg_cpu_temp = cal_temp_reader.avg_cpu_temp()
        instant_sensor_temp = cal_temp_reader.instant_sensor_temp()
        avg_cal_temp = cal_temp_reader.avg_calibrated_temp()
        print "\t".join([str(round(x,1)) for x in [instant_cpu_temp, avg_cpu_temp, instant_sensor_temp, avg_cal_temp]])
        time.sleep(0.5)
    print "Stopping main"

if __name__ == "__main__":
    main()


