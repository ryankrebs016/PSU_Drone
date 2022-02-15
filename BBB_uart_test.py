import Adafruit_BBIO.UART as UART
import Adafruit_BBIO.GPIO as GPIO
import serial
import numpy
import time


UART.setup("UART1")
GPIO.setup("P8_14",GPIO.OUT)
GPIO.setup("P8_16",GPIO.IN)
GPIO.output("P8_14",GPIO.LOW)
ser=serial.Serial(port='/dev/tty01',baudrate=115200)
send=0b01010101
ser.write(send)
time.sleep(.01)
rec=ser.read(1)
print('rec=send',send==rec)

print(GPIO.input("P8_16"))
GPIO.output("P8_14",GPIO.HIGH)
print(GPIO.input("P8_16"))
