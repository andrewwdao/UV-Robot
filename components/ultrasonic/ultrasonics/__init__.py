from ultrasonics.ultrasonics import Ultrasonics

PORT = '/dev/ttyUSB0'
BAUDRATE = 9600

sensor = Ultrasonics(BAUDRATE)
# sensor = Ultrasonics(PORT, BAUDRATE)
