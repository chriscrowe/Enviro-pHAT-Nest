#!/usr/bin/env python
from __future__ import division

import time

from ISStreamer.Streamer import Streamer

from constants import *
from enviro_temp.temp_reader import CalibratedTempReader


class MyStreamer(object):

    def __init__(self, bucket_name, bucket_key, access_key):
        pass # TODO: Customized loggers for each temp type


def main():
    is_streamer = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)
    cal_temp_reader = CalibratedTempReader(calibration_factor=1.1)
    try:
        while True:
            instant_cpu_temp = cal_temp_reader.cpu_temp()
            avg_cpu_temp = cal_temp_reader.avg_cpu_temp()
            instant_sensor_temp = cal_temp_reader.sensor_temp()
            avg_cal_temp = cal_temp_reader.avg_calibrated_temp()

            is_streamer.log(INSTANT_CPU_TEMP_LABEL, str("{0:.2f}".format(instant_cpu_temp)))
            is_streamer.log(AVG_CPU_TEMP_LABEL, str("{0:.2f}".format(avg_cpu_temp)))

            is_streamer.log(SENSOR_TEMP_LABEL, str("{0:.2f}".format(instant_sensor_temp)))
            is_streamer.log(AVG_CALIBRATED_TEMP_LABEL, str("{0:.2f}".format(avg_cal_temp)))
            is_streamer.flush()
            time.sleep(SECONDS_BETWEEN_READS)
    except KeyboardInterrupt:
        cal_temp_reader.stop_thread()

if __name__ == "__main__":
    main()