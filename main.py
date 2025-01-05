import RPi.GPIO as GPIO
import time
import pcprox
from datetime import datetime
from cardreader import CardReader

# Define pin names
PIN_DEVICE_POWER = 7
PIN_STATUS_UV = 8

transition = 0

# Set up GPIO mode
GPIO.setmode(GPIO.BOARD)

# Set GPIO pin 7 as an output pin
GPIO.setup(PIN_DEVICE_POWER, GPIO.OUT)

# Set GPIO pin 8 as an input PULLUP pin
GPIO.setup(PIN_STATUS_UV, GPIO.IN, pull_up_down=GPIO.PUD_UP)



# Define the interrupt callback function
def uv_led_detected(channel):
    global transition  # a Reference to the same variable above
    cycle_complete = False
    
    state_uv_cur = GPIO.input(PIN_STATUS_UV)
    on_off_status = ''
    if state_uv_cur == GPIO.LOW:
        on_off_status = 'ON'  # The LEDs were OFF but got turned on
        if transition == 0:
            transition = 1
        else:
            # Something weird happened, reset.
            transition = 0
    else:
        on_off_status = 'OFF' # The LEDs were ON but got turned OFF
        if transition == 1:
            transition = 0
            cycle_complete = True
        else:
            # Something weird happened, reset.
            transition = 0 

    print(f"UV LEDs {on_off_status}: ", get_current_time())
    
    if cycle_complete:
        print(f"Cycle Complete.\n")
    




# Set up an interrupt for rising OR falling edge
GPIO.add_event_detect(PIN_STATUS_UV, GPIO.BOTH, callback=uv_led_detected, bouncetime=300)



def main(debug=False):
    
    current_time = get_current_time()
    print('Script started at ',current_time)
    
    
    # Setup the card reader by instantiating a CardReader
    card_reader = CardReader()
    
    print('Waiting for a card...')
    try:
        while True:
            # Scan for tags forever
            tag = card_reader.scan_for_tags()
            
            # If we got a tag, print it out
            if tag is not None:
                print('Tag data: %s' % pcprox._format_hex(tag[0]))
                print('Bit length: %d' % tag[1])
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()  # Clean up GPIO pins



def get_state(pin):
    return GPIO.input(pin)


def get_current_time():
    return datetime.now().replace(microsecond=0).isoformat()


def test_LED():
    GPIO.output(PIN_DEVICE_POWER, GPIO.LOW)
    time.sleep(2)
    GPIO.output(PIN_DEVICE_POWER, GPIO.HIGH)
    time.sleep(2)


def blink():
    GPIO.output(PIN_DEVICE_POWER, GPIO.HIGH)   # Turn on
    time.sleep(1)
    GPIO.output(PIN_DEVICE_POWER, GPIO.LOW)    # Turn off
    time.sleep(1)


if __name__ == '__main__':
    main()
