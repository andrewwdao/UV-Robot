from ultrasonics import sensor
import time

while True:
    print(sensor.read())
    time.sleep(0.5)
