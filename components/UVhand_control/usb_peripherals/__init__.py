from usb_peripherals.ultrasonics import Ultrasonics
from usb_peripherals.motor import MotorUART_PWM#, MotorUART_PID

SENSOR_BAUDRATE = 9600
MOTOR_BAUDRATE = 250000
MAX_SPEED = 600

sensor = Ultrasonics(SENSOR_BAUDRATE)
# sensor = Ultrasonics(PORT, BAUDRATE)
motor = MotorUART_PWM(sensor.port, MOTOR_BAUDRATE, MAX_SPEED)
# Motor = MotorUART_PWM(PORT, BAUDRATE, MAX_SPEED)

