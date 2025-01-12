import RPi.GPIO as GPIO
import time
import pcprox
from datetime import datetime
from cardreader import CardReader

# Define pin names
PIN_STATUS_DEVICE = 32
PIN_STATUS_UV = 36
PIN_STATUS_DOOR_RED = 38
PIN_STATUS_DOOR_GREEN = 40

transition = 0

# Define states for the FSM
IDLE = 0
DISINFECTING = 1

state = None
previous_state = None
device_active = False

# Card Reader to be used
card_reader = None


def exit_state(old_state,new_state):
    pass


def enter_state(new_state,old_state):
    if new_state == IDLE:
        print('Idling')
    elif new_state == DISINFECTING:
        print('Disinfecting')


def get_transition():
    global state
    global device_active
    # Figure out what to do next based on state variables
    if state == IDLE:
        if device_active == True:
            return DISINFECTING
    elif state == DISINFECTING:
        if device_active == False:
            return IDLE
    
    return None


def state_logic():
    global state
    
    _check_device_status()
    if state == IDLE:
        _idle()
    elif state == DISINFECTING:
        _disinfecting()


def set_state(new_state):
    global state
    previous_state = state
    state = new_state
    if previous_state != None:
        exit_state(previous_state, new_state)
    if new_state != None:
        enter_state(new_state, previous_state)


def _idle():
    global card_reader
    
    # Scan for tags forever
    tag = card_reader.scan_for_tags()
    
    # If we got a tag, print it out
    if tag is not None:
        print('Tag data: %s' % pcprox._format_hex(tag[0]))
        print('Bit length: %d' % tag[1])
    time.sleep(0.5)

def _disinfecting():
    pass

def _check_device_status():
    global device_active
    if GPIO.input(PIN_STATUS_DEVICE) == GPIO.LOW:
        device_active = True
    else:
        device_active = False
        



# Report details
badge_details = [True, 12345, 'JOHN DOE']
time_device_active = [None,None]
time_uv_leds = [None, None]
time_green_led = [None, None]
time_red_led = [None, None]

# Set up GPIO mode
GPIO.setmode(GPIO.BOARD)



# Set GPIO pin modes
GPIO.setup(PIN_STATUS_DEVICE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_STATUS_UV, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_STATUS_DOOR_RED, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_STATUS_DOOR_GREEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)



# Define the interrupt callback function
def int_device_active(channel):
    
    time.sleep(0.5)
    global transition  # a Reference to the same variable above
    cycle_complete = False
    
    state_dev_cur = GPIO.input(PIN_STATUS_DEVICE)
    on_off_status = ''
    if state_dev_cur == GPIO.LOW:
        on_off_status = 'ON'  # The LEDs were OFF but got turned on
        if transition == 0:
            transition = 1
            time_device_active[0] = get_current_time()
            print('Cycle started...')
        else:
            # Something weird happened, reset.
            transition = 0
    else:
        on_off_status = 'OFF' # The LEDs were ON but got turned OFF
        if transition == 1:
            transition = 0
            time_device_active[1] = get_current_time()
            cycle_complete = True
        else:
            # Something weird happened, reset.
            transition = 0 

    #print(f"UV LEDs {on_off_status}: ", get_current_time())
    if cycle_complete:
        new_report = create_report(badge_details, time_uv_leds,time_green_led, time_red_led)
        print(new_report)
        clear_report_details()


def int_led_uv(channel):
    state_led_uv = GPIO.input(PIN_STATUS_UV)
    if state_led_uv == GPIO.LOW:
        time_uv_leds[0] = get_current_time()
    else:
        time_uv_leds[1] = get_current_time()
    

def int_door_led_green(channel):
    state_led = GPIO.input(PIN_STATUS_DOOR_GREEN)
    if state_led == GPIO.LOW:
        time_green_led[0] = get_current_time()
    else:
        time_green_led[1] = get_current_time()


def int_door_led_red(channel):
    state_led = GPIO.input(PIN_STATUS_DOOR_RED)
    if state_led == GPIO.LOW:
        time_red_led[0] = get_current_time()
    else:
        time_red_led[1] = get_current_time()


# Set up an interrupt for rising OR falling edge
GPIO.add_event_detect(PIN_STATUS_DEVICE, GPIO.BOTH, callback=int_device_active, bouncetime=300)
GPIO.add_event_detect(PIN_STATUS_UV, GPIO.BOTH, callback=int_led_uv, bouncetime=300)
GPIO.add_event_detect(PIN_STATUS_DOOR_GREEN, GPIO.BOTH, callback=int_door_led_green, bouncetime=300)
GPIO.add_event_detect(PIN_STATUS_DOOR_RED, GPIO.BOTH, callback=int_door_led_red, bouncetime=300)


"""
clear_report_details
"""
def clear_report_details():
    badge_details = [True, 12345, 'JOHN DOE']
    time_device_active = [None, None]
    time_uv_leds = [None, None]
    time_green_led = [None, None]
    time_red_led = [None, None]


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
    cycle_time = (time_device_active[1] - time_device_active[0]).total_seconds()
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
    


def main(debug=False):
    global card_reader
    current_time = get_current_time()
    print('Script started at ',current_time)
    
    
    # Setup the card reader by instantiating a CardReader
    card_reader = CardReader(debug=False)
    
    print('Waiting for a card...')
    
    set_state(IDLE)
    try:
        while True:
            if state != None:
                state_logic()
                trans = get_transition()
                if trans != None:
                    set_state(trans)
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
