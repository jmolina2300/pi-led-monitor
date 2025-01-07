import RPi.GPIO as GPIO
import time
import pcprox
from datetime import datetime
from cardreader import CardReader

# Define pin names
PIN_DEVICE_POWER = 7
PIN_STATUS_UV = 8

transition = 0


# Report details
badge_details = [True, 12345, 'JOHN DOE']
time_uv_leds = [None, None]
time_green_led = [None, None]
time_red_led = [None, None]

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
            time_uv_leds[0] = get_current_time()
            time_green_led[1] = time_uv_leds[0]
            time_red_led[0] = time_uv_leds[0]
        else:
            # Something weird happened, reset.
            transition = 0
    else:
        on_off_status = 'OFF' # The LEDs were ON but got turned OFF
        if transition == 1:
            transition = 0
            time_uv_leds[1] = get_current_time()
            time_green_led[0] = time_uv_leds[1]
            time_red_led[1] = time_uv_leds[1]
            cycle_complete = True
        else:
            # Something weird happened, reset.
            transition = 0 

    #print(f"UV LEDs {on_off_status}: ", get_current_time())
    if cycle_complete:
        new_report = create_report(badge_details, time_uv_leds,time_green_led, time_red_led)
        print(new_report)

"""
is_cycle_complete

Tells if a cycle was complete based on the duration (~35 seconds).
Placeholder.

"""
def is_complete_cycle(duration):
    if duration >= 25:
        return True
    else:
        return False


"""
create_report

Creates a report with the badge ID, the time ON/OFF for all  LEDs and 
any other information required.


Parameter format:
  badge_details[badge_id_read, badge_id, badge_name]
  time_uv_leds[time_ON, time_OFF]
  time_green_led[time_ON, time_OFF]
  time_red_led[time_ON, time_OFF]

"""
def create_report(badge_details,time_uv_leds, time_green_led, time_red_led):
    current_time = get_current_time()
    cycle_time = (time_uv_leds[1] - time_uv_leds[0]).total_seconds()
    complete_cycle = is_complete_cycle(cycle_time)
    report = '************************************************\n'
    report += f"Date: {current_time}\n"
    report += f"Badge ID Read: {badge_details[0]}\n"
    report += f"Badge ID Number: {badge_details[1]}\n"
    report += f"Name: {badge_details[2]}\n"
    report += '************************************************\n'
    report += f"Upper LEDs ON: {time_uv_leds[0]}\n"
    report += f"Upper LEDs OFF: {time_uv_leds[1]}\n"
    report += f"Door Green LED ON: {time_green_led[0]}\n"
    report += f"Door Green LED OFF: {time_green_led[1]}\n"
    report += f"Door Red LED ON: {time_red_led[0]}\n"
    report += f"Door Red LED OFF: {time_red_led[1]}\n"
    report += '************************************************\n'
    report += f"Cycle complete: {complete_cycle}\n"
    report += f"Cycle time: {cycle_time}\n\n"
    return report
    



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


def get_current_time_iso():
    return datetime.now().replace(microsecond=0).isoformat()
    
def get_current_time():
    return datetime.now().replace(microsecond=0)


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
