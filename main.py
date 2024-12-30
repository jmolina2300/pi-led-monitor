import RPi.GPIO as GPIO
import time
from datetime import datetime


# Define pin names
PIN_DEVICE_POWER = 7

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Set GPIO pin 17 as an output pin
GPIO.setup(PIN_DEVICE_POWER, GPIO.OUT)




def main():
    current_time = get_current_time()
    print('Script started at ',current_time)
	
	GPIO.output(PIN_DEVICE_POWER, GPIO.LOW)
	time.sleep(2)
	GPIO.output(PIN_DEVICE_POWER, GPIO.HIGH)
	time.sleep(2)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()  # Clean up GPIO pins


def get_current_time():
    return datetime.now().replace(microsecond=0).isoformat()


def blink():
    GPIO.output(PIN_DEVICE_POWER, GPIO.HIGH)   # Turn on
    time.sleep(1)
    GPIO.output(PIN_DEVICE_POWER, GPIO.LOW)    # Turn off
    time.sleep(1)


if __name__ == '__main__':
    main()
