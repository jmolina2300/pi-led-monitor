import RPi.GPIO as GPIO
import time
from datetime import datetime


# Define pin names
PIN_LED_BLUE = 7

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Set GPIO pin 17 as an output pin
GPIO.setup(PIN_LED_BLUE, GPIO.OUT)




def main():
    current_time = get_current_time()
    print('Script started at ',current_time)
    try:
        while True:
            blink()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()  # Clean up GPIO pins

def get_current_time():
    return datetime.now().replace(microsecond=0).isoformat()

def blink():
    GPIO.output(PIN_LED_BLUE, GPIO.HIGH)   # Turn on LED
    time.sleep(1)
    GPIO.output(PIN_LED_BLUE, GPIO.LOW)    # Turn off LED
    time.sleep(1)


if __name__ == '__main__':
    main()
