import os

BUCKET_NAME = "Averaged Enviro PHAT"
BUCKET_KEY = os.environ['IS_BUCKET_KEY']
ACCESS_KEY = os.environ['IS_ACCESS_KEY']
SENSOR_NAME = "Enviro PHAT"

# Set the time between sensor reads
SECONDS_BETWEEN_READS = 1
METRIC_UNITS = False

INSTANT_CPU_TEMP_LABEL = "Instant CPU Temperature(F)"
AVG_CPU_TEMP_LABEL = "Avg CPU Temperature(F)"
AVG_CALIBRATED_TEMP_LABEL = "Avg Calibrated {} Temperature(F)".format(SENSOR_NAME)
SENSOR_TEMP_LABEL = "Instant {} Temperature(F)".format(SENSOR_NAME)