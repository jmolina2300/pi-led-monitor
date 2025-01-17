import RPi.GPIO as GPIO
import time
import pcprox
from datetime import datetime
from cardreader import CardReader

# Define pin names
PIN_STATUS_DEVICE = 32
PIN_STATUS_UV = 36
PIN_STATUS_DOOR_GREEN = 38
PIN_STATUS_DOOR_RED = 40



# Set up GPIO mode
GPIO.setmode(GPIO.BOARD)

# Set GPIO pin modes
GPIO.setup(PIN_STATUS_DEVICE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_STATUS_UV, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_STATUS_DOOR_RED, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_STATUS_DOOR_GREEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


status_device = GPIO.input(PIN_STATUS_DEVICE)
status_uv = GPIO.input(PIN_STATUS_UV)
status_door_red = GPIO.input(PIN_STATUS_DOOR_RED)
status_door_green = GPIO.input(PIN_STATUS_DOOR_GREEN)
print('PIN_DEVICE',status_device)
print('PIN_UV',status_uv)
print('PIN_DOOR_RED',status_door_red)
print('PIN_DOOR_GREEN',status_door_green)
print('')

device_idling = (status_door_red == GPIO.HIGH) and (status_door_green == GPIO.LOW)
device_disinfecting = (status_door_red == GPIO.LOW) and (status_door_green == GPIO.HIGH) and (status_uv == GPIO.LOW)
if device_idling:
  print("Device is IDLING")
elif device_disinfecting:
  print("Device is DISINFECTING")
else:
  print("Error: Device in an undefined state.")
print('')

GPIO.cleanup()
