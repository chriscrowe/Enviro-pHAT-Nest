import argparse
import logging
import time

import sys

from enviro_temp.calibrated_temp_reader import CalibratedTempReader


def main(as_tsv=False, rolling_avg_window=3, calibration_factor=1.3):
    cal_temp_reader = CalibratedTempReader(calibration_factor=calibration_factor, rolling_avg_window=rolling_avg_window)
    cal_temp_reader.logger.setLevel(logging.ERROR)

    if as_tsv:
        print "Instant CPU\tAvg CPU\tInstant Sensor\tOffset Sensor\tAvg Offset Sensor\tAvg Sensor (Calibrated)\tOffset-Cal"

    while cal_temp_reader.is_running():
        instant_cpu_temp = cal_temp_reader.cpu_temp()
        avg_cpu_temp = cal_temp_reader.avg_cpu_temp()
        instant_sensor_temp = cal_temp_reader.sensor_temp()
        avg_sensor_temp = cal_temp_reader.avg_sensor_temp()
        avg_cal_temp = cal_temp_reader.avg_calibrated_temp()
        delta = avg_sensor_temp - avg_cal_temp

        if as_tsv:
            print "\t".join([str(round(x, 1)) for x in [instant_cpu_temp, avg_cpu_temp, instant_sensor_temp, avg_cal_temp, delta]])
        else:
            print "\033c"

            sys.stdout.write(
                       "Instant CPU:       {instant_cpu:.1f}\n" \
                       "Avg CPU:           {avg_cpu:.1f}\n" \
                       "Instant Sensor:    {instant_sensor:.1f}\n" \
                       "Avg Cal Sensor:    {avg_sensor:.1f}\n" \
                       "Sensor-Cal Delta:        {delta}".format(
                instant_cpu=instant_cpu_temp,
                avg_cpu=avg_cpu_temp,
                instant_sensor=instant_sensor_temp,
                avg_sensor=avg_cal_temp,
                delta=delta,
            ))
            sys.stdout.flush()

        time.sleep(0.5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script for debugging temperature readings and finding the right constants for calibration.')

    parser.add_argument("--as-tsv", help="Print out the temp values in a tab-separated values format", action='store_true')
    parser.add_argument("--avg-window", help="Size of the rolling average windows (default=5)", type=int, default=5)
    parser.add_argument("--cal-factor", help="Calibration constant for the CPU-temp based calibration (default=1.3)", type=float, default=1.3)

    args = parser.parse_args()

    main(
        as_tsv=args.as_tsv,
        calibration_factor=args.cal_factor,
        rolling_avg_window=args.avg_window
    )




