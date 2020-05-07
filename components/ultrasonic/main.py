from ultrasonics import sensor
import time

while True:
    sensor.read()
    time.sleep(0.5)
