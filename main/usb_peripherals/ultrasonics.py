"""------------------------------------------------------------*-
  Module for Ultrasonic sensors
  Tested on: Raspberry Pi 3B/3B+
  (c) Minh-An Dao 2020
  version 1.00 - 07/05/2020
 --------------------------------------------------------------
 * Module created for the purpose of controlling the movement
 * of the UV robot.
 * Specifically designed for MSD_EM modules
 *
 * ref: https://www.robot-electronics.co.uk/htm/srf05tech.htm
 *
 --------------------------------------------------------------"""
import os
import serial
import struct
import time


millis = lambda: int(time.time() * 1000)

class Ultrasonics(object):
    """
    A python written library for the MSD_EM motor driver module.

    @attribute Serial __serial
    UART serial connection via PySerial.
    """

    def __init__(self, baudRate=9600):
        """
        Constructor
        @param port: a string dedicated to the connected device
        @param baudRate: an integer indicates the connection spped
        """
        if baudRate < 9600 or baudRate > 1000000:
            raise ValueError('The given baudrate is invalid!')

        self.port = '/dev/ttyUSB0'
        try:
            for i in range(0,2):
                
                self.port = self.port[:11] + str(i)
                print(self.port) 

                # Initialize PySerial connection
                self.__serial = serial.Serial(port=self.port,
                                            baudrate=baudRate,
                                            bytesize=serial.EIGHTBITS, 
                                            timeout=2
                                            )

                if self.__serial.isOpen():
                    self.__serial.close()
                self.__serial.open()

                if len(self.read()) is 7:
                    print("Ultrasonic ready!")
                    return
                
                self.__serial.close()

            # raise ValueError("Port existed but no sensor is connected! Please check your wiring")
        except:
            self.port = 'Not Connected'
            print("No sensor is connected! Please check your wiring")
            return
        
    def read(self):
        try:
            self.__serial.flushInput()
            data = self.__serial.readline().decode('utf-8').split(" ")
            return data
        except:
            return [999,999,999,999,999,999] # return for not connected

