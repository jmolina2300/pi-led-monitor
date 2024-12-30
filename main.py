import RPi.GPIO as GPIO
import time
from datetime import datetime


# Define pin names
PIN_DEVICE_POWER = 7
PIN_STATUS_UV = 8


# Set up GPIO mode
GPIO.setmode(GPIO.BCM)


# Set GPIO pin 7 as an output pin
GPIO.setup(PIN_DEVICE_POWER, GPIO.OUT)

# Set GPIO pin 8 as an input PULLUP pin
GPIO.setup(PIN_STATUS_UV, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define the interrupt callback function
def uv_led_detected(channel):
    state_uv_cur = GPIO.input(PIN_STATUS_UV)
    on_off_status = ''
    if state_uv_cur == GPIO.LOW:
        on_off_status = 'ON'  # The LEDs were OFF but got turned on
    else:
        on_off_status = 'OFF' # The LEDs were ON but got turned OFF
    
    print(f"UV LEDs {on_off_status}: ", get_current_time())

# Set up an interrupt for rising OR falling edge
GPIO.add_event_detect(PIN_STATUS_UV, GPIO.BOTH, callback=uv_led_detected, bouncetime=300)


def main():
    current_time = get_current_time()
    print('Script started at ',current_time)
	
    GPIO.output(PIN_DEVICE_POWER, GPIO.LOW)
    time.sleep(2)
    GPIO.output(PIN_DEVICE_POWER, GPIO.HIGH)
    time.sleep(2)
    try:
        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()  # Clean up GPIO pins

def get_state(pin):
    return GPIO.input(pin)
    
def get_current_time():
    return datetime.now().replace(microsecond=0).isoformat()


def blink():
    GPIO.output(PIN_DEVICE_POWER, GPIO.HIGH)   # Turn on
    time.sleep(1)
    GPIO.output(PIN_DEVICE_POWER, GPIO.LOW)    # Turn off
    time.sleep(1)


if __name__ == '__main__':
    main()
