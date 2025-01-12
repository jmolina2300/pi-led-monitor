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


CYCLE_TIME_EXPECTED = 26

# Define states for the FSM
IDLE = 0
DISINFECTING = 1

state = None
previous_state = None
device_active = False

state_door_green_led = 0
state_door_green_led_prev = 0

state_door_red_led = 0
state_door_red_led_prev = 0

door_green_led_need_transition = False
door_red_led_need_transition = False
uv_led_need_transition = False


status_uv_leds = None
status_uv_leds_prev = None


# Card Reader to be used
card_reader = None


# Report details
badge_details = [False, 0, ' ']
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



def exit_state(old_state,new_state):
    if old_state == DISINFECTING:
        time_device_active[1] = get_current_time()
        fix_uv_led_time()
        new_report = create_report(badge_details, time_uv_leds,time_green_led, time_red_led)
        print(new_report)
        clear_report_details()
    


def enter_state(new_state,old_state):
    if new_state == IDLE:
        clear_report_details()
        print('Idling')
    elif new_state == DISINFECTING:
        time_device_active[0] = get_current_time()
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
        _check_door_leds()
        _check_uv_leds()
        _disinfecting()


def set_state(new_state):
    global state, previous_state
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
    #time.sleep(0.4)


def _disinfecting():
    #time.sleep(0.4) # Must delay a little bit
    pass


def _check_device_status():
    global device_active
    if GPIO.input(PIN_STATUS_DEVICE) == GPIO.LOW:
        device_active = True
    else:
        device_active = False


def _check_door_leds():
    global door_red_led_need_transition
    global door_green_led_need_transition
    global time_red_led, time_green_led
    
    
    
    if door_red_led_need_transition:
        status_red_led = GPIO.input(PIN_STATUS_DOOR_RED)
        if status_red_led == GPIO.LOW:
            time_red_led[0] = get_current_time()
        else:
            time_red_led[1] = get_current_time()
        door_red_led_need_transition = False
    
    if door_green_led_need_transition:
        status_green_led = GPIO.input(PIN_STATUS_DOOR_GREEN)
        if status_green_led == GPIO.LOW:
            time_green_led[0] = get_current_time()
        else:
            time_green_led[1] = get_current_time()
        door_green_led_need_transition = False
            

def _check_uv_leds():
    global status_uv_leds, status_uv_leds_prev
    
    status_uv_leds = GPIO.input(PIN_STATUS_UV)
    need_transition = (status_uv_leds != status_uv_leds_prev)
    if need_transition:
        status_uv_leds_prev = status_uv_leds
        if status_uv_leds == GPIO.LOW:
            time_uv_leds[0] = get_current_time()
            print("UV LEDs ON")
        else:
            print("UV LEDs OFF")
            time_uv_leds[1] = get_current_time()
            
            # Maybe don't need to worry about the OFF time because they
            #  automatically turn off when the device itself turns off.
            pass

"""
fix_uv_led_time

Fixs the UV LED time. If the LEDs are working properly, they turn OFF
at the same time as the device itself, which makes logging their own 
OFF time very tricky.

This function compares the OFF time to the ON time, and makes sure it
sits somewhere in the middle, OR, if everything worked fine, at the 
very end. 

"""
def fix_uv_led_time():
    global time_uv_leds
    
    uv_malfunction = (time_uv_leds[0] == None or time_uv_leds[1] == None)
    if uv_malfunction:
        return
    
    impossibly_early = (time_uv_leds[1] < time_uv_leds[0])
    impossibly_exact = (time_uv_leds[1] == time_uv_leds[0]) 
    impossible_time = impossibly_exact or impossibly_early
    leds_turned_on = time_uv_leds[0] != None
    
    if leds_turned_on:
        if impossible_time:
            # The LEDs must have shut off at the same time as the device.
            time_uv_leds[1] = get_current_time()
        
    

def int_led_uv(channel):
    global uv_led_need_transition
    uv_led_need_transition = True
    

def int_door_led_green(channel):
    global door_red_led_need_transition
    global door_green_led_need_transition
    door_green_led_need_transition = True


def int_door_led_red(channel):
    global door_red_led_need_transition
    global door_green_led_need_transition
    door_red_led_need_transition = True


# Set up an interrupt for rising OR falling edge
GPIO.add_event_detect(PIN_STATUS_UV, GPIO.BOTH, callback=int_led_uv, bouncetime=250)
GPIO.add_event_detect(PIN_STATUS_DOOR_GREEN, GPIO.BOTH, callback=int_door_led_green, bouncetime=250)
GPIO.add_event_detect(PIN_STATUS_DOOR_RED, GPIO.BOTH, callback=int_door_led_red, bouncetime=250)


"""
clear_report_details
"""
def clear_report_details():
    global badge_details
    global time_device_active
    global time_uv_leds
    global time_green_led
    global time_red_led
    badge_details = [False, 0, ' ']
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
    uv_time = (time_uv_leds[1] - time_uv_leds[0]).total_seconds()
    complete_cycle = is_complete_cycle(cycle_time)
    report = '************************************************\n'
    report += f"Date: {current_time}\n"
    report += f"Badge ID Read: {badge_details[0]}\n"
    report += f"Badge ID Number: {badge_details[1]}\n"
    report += f"Name: {badge_details[2]}\n"
    report += '************************************************\n'
    report += f"UV LEDs ON: {time_uv_leds[0]}\n"
    report += f"UV LEDs OFF: {time_uv_leds[1]}\n"
    report += f"Door Green LED ON: {time_green_led[0]}\n"
    report += f"Door Green LED OFF: {time_green_led[1]}\n"
    report += f"Door Red LED ON: {time_red_led[0]}\n"
    report += f"Door Red LED OFF: {time_red_led[1]}\n"
    report += '************************************************\n'
    report += f"Cycle complete: {complete_cycle}\n"
    report += f"Cycle time: {cycle_time}\n"
    report += '************************************************\n'
    
    uv_led_status = get_diagnostic_uv_leds(time_uv_leds,cycle_time)
    door_green_led_status = get_diagnostic_door_leds(time_green_led,cycle_time)
    door_red_led_status = get_diagnostic_door_leds(time_red_led,cycle_time)

    report += f"HARDWARE SELF-CHECK                            \n"
    report += f"UV LED status: {uv_led_status}                 \n"
    report += f"Door Green LED status: {door_green_led_status} \n"
    report += f"Door Red LED status: {door_green_led_status} \n\n"
    
    
    return report


def get_diagnostic_uv_leds(time_on_off,cycle_time):
    uv_leds_dead = (time_on_off[1] == None and time_on_off[0] == None)
    if uv_leds_dead:
        return 'CRITICAL. LEDs NOT DETECTED. REPLACE LEDs OR SENSOR.'
    
    uv_led_status = ''
    invalid_time = (time_on_off[1] == None or time_on_off[0] == None)
    uv_duration = (time_on_off[1] - time_on_off[0]).total_seconds()
    short_cycle = (uv_duration < CYCLE_TIME_EXPECTED) and (uv_duration < cycle_time - 1.5)
    
    if invalid_time:
        uv_led_status = 'WARNING. INVALID TIME. CHECK LEDs OR SENSOR.'
    elif short_cycle:
        uv_led_status = 'WARNING. LEDs TURNED OFF PREMATURELY.'
    else:
        uv_led_status = 'OK.'
    
    return uv_led_status


def get_diagnostic_door_leds(time_on_off,cycle_time):
    leds_dead = (time_on_off[1] == None and time_on_off[0] == None)
    if leds_dead:
        return 'CRITICAL. LEDs NOT DETECTED. REPLACE LEDs OR SENSOR.'
    
    led_status = ''
    invalid_time = (time_on_off[1] == None or time_on_off[0] == None)
    duration = abs((time_on_off[1] - time_on_off[0]).total_seconds())
    short_cycle = (duration < CYCLE_TIME_EXPECTED) and (duration < cycle_time)
    
    if invalid_time:
        led_status = 'WARNING. INVALID TIME. CHECK LEDs OR SENSOR.'
    elif short_cycle:
        led_status = 'WARNING. LEDs TURNED OFF PREMATURELY.'
        print(duration)
    else:
        led_status = 'OK.'
    
    return led_status
    

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
            time.sleep(0.1) # Must delay a little bit
            if state != None:
                state_logic()
                trans = get_transition()
                if trans != None:
                    set_state(trans)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()  # Clean up GPIO pins




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
