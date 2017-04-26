#!/usr/bin/env python
import argparse
import logging

import time

from enviro_temp.temp_reader import CalibratedTempReader
from my_nest import MyNest


class EnviroNestControl(object):

    def __init__(self, low_temp, high_temp, activate_margin, stop_margin, refresh_rate, dummy_nest=False):
        self.low_temp = low_temp
        self.high_temp = high_temp
        self.activate_margin = activate_margin
        self.stop_margin = stop_margin
        self.refresh_rate = refresh_rate

        self.logger = logging.getLogger("enviro_nest_control")
        self.mynest = MyNest(dummy_mode=dummy_nest)
        self.mynest.logger.setLevel(logging.DEBUG)
        self.temp_reader = CalibratedTempReader()
        self.temp_reader.logger.setLevel(logging.DEBUG)


    def run(self):
        is_running = False
        target = None
        while True:
            curr_temp = self.temp_reader.avg_calibrated_temp()
            if target is not None and curr_temp ==  target:
                # We hit our target-- reset back to the original polling loop
                is_running = False
            elif not is_running:
                if curr_temp <= self.low_temp - self.activate_margin:
                    target = self.low_temp + self.stop_margin
                    self.logger.info("Current temp {} below low threshold {}, setting target to {}".format(curr_temp, self.low_temp, target))
                    self.mynest.set_target_temp(target)
                    is_running = True
                elif curr_temp >= self.high_temp + self.activate_margin:
                    target = self.high_temp - self.stop_margin
                    self.logger.info("Current temp {} above high threshold {}, setting target to {}".format(curr_temp, self.high_temp, target))
                    self.mynest.set_target_temp(target)
                    is_running = True
                    self.logger.debug("Sleeping for {} seconds".format(self.refresh_rate))
        time.sleep(self.refresh_rate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Use Enviro pHAT temperature and Nest to maintain temp range.')

    parser.add_argument(dest="low_temp", help="Lowest acceptable temp (in Fahrenheit)", type=int)
    parser.add_argument(dest="high_temp", help="Highest acceptable temp (in Fahrenheit)", type=int)

    parser.add_argument("--refresh-rate", help="Rate for polling temp from Enviro pHAT (in Hz, default=60)", type=int, default=60)
    parser.add_argument("--activate-margin", help="How many outside of the target range before start heating/cooling? (default=1)", type=int, default=1)
    parser.add_argument("--stop-margin", help="How many insde of the target range before stop heating/cooling? (default=2)", type=int, default=2)
    parser.add_argument("--dummy-nest", help="Use this for testing in order to not get throttled by the Nest API", type=bool, action='store_true')

    args = parser.parse_args()

    control = EnviroNestControl(
        args.low_temp,
        args.high_temp,
        args.activate_margin,
        args.stop_margin,
        args.refresh_rate,
        dummy_nest=False
    )

    control.run()