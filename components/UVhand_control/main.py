from usb_peripherals import sensor, motor
import time

while True:
    sensorval = sensor.read()
    print(sensorval)
    if int(sensorval[0]) > 70: # if sensor is greater than 100cm 
        motor.Lhand_up()
    else:
        motor.Lhand_stop()
    time.sleep(0.5)
