#!/usr/bin/env python

import time

from envirophat import weather, leds


print("""This example will detect motion using the accelerometer.

Press Ctrl+C to exit.

""")

threshold = None

try:
    while True:
        celsius = weather.temperature()

        if threshold is None:
            threshold = celsius + 2

        fahrenheit = 9.0 / 5.0 * celsius + 32

        print("{}* F".format(fahrenheit))
        if celsius > threshold:
            leds.on()
        else:
            leds.off()

        time.sleep(0.1)

except KeyboardInterrupt:
    pass


