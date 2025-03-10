#!/usr/bin/env python3


import RPi.GPIO as GPIO
import time
import pcprox
from datetime import datetime
from cardreader import CardReader
from badge import Badge

# Define pin names
PIN_DEVICE = 32
PIN_UV_LED = 36
PIN_DOOR_GREEN_LED = 38
PIN_DOOR_RED_LED = 40

# Define an 'expected' cycle time to determine if the cycle was compliant
CYCLE_TIME_EXPECTED = 26

# Define states for the FSM
IDLE = 0
DISINFECTING = 1

# STATE: DEVICE
state = None
previous_state = None
device_active = False



# STATE: UV LEDs
state_uv_leds = None
state_uv_leds_prev = None

# STATE: DOOR RED LED
state_door_red_led = None
state_door_red_led_prev = None

# STATE: DOOR GREEN LED
state_door_green_led = None
state_door_green_led_prev = None

# DATA: Card Reader
data_RFID = None
data_RFID_prev = None


# Card Reader object to be used
card_reader = None


# Report details -- Probably turn this into a data structure
badge = None
time_device_active = [None,None]
time_uv_leds = [None, None]
time_door_green_led = [None, None]
time_door_red_led = [None, None]


# Set up GPIO mode
GPIO.setmode(GPIO.BOARD)



# Set GPIO pin modes
GPIO.setup(PIN_DEVICE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_UV_LED, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_DOOR_RED_LED, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_DOOR_GREEN_LED, GPIO.IN, pull_up_down=GPIO.PUD_UP)


"""
exit_state

Called ONCE when exiting a state.

"""
def exit_state(old_state,new_state):
    global time_device_active
    
    if old_state == DISINFECTING:
        time_device_active[1] = get_current_time()
        fix_uv_led_time()
        new_report = create_report()
        print(new_report)
        clear_report_details()
    

"""
exit_state

Called ONCE when entering a new state.

"""
def enter_state(new_state,old_state):
    global time_device_active
    
    if new_state == IDLE:
        clear_report_details()
        print('Idling')
    elif new_state == DISINFECTING:
        time_device_active[0] = get_current_time()
        print('Disinfecting')


"""
get_transition

Called always.

This function determines what state to transition into based on the value of
some flag variables. In our simple case, there is only 1 variable:

    device_active

Return value is a state to transition into. Sometimes, there won't be a
transition. In that case, the 'if-else' block will be avoided and the function
will return None.


"""
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


"""
state_logic

Called always.

This function performs the actions associated with each state.

"""
def state_logic():
    global state
    
    _check_device_status()
    if state == IDLE:
        _idle()
    elif state == DISINFECTING:
        _check_door_leds()
        _check_uv_leds()
        _disinfecting()


"""
set_state

Called at startup (manually) and called each time a transition is needed.

"""
def set_state(new_state):
    global state, previous_state
    previous_state = state
    state = new_state
    if previous_state != None:
        exit_state(previous_state, new_state)
    if new_state != None:
        enter_state(new_state, previous_state)
 

"""
handle_tag_read

Called ONCE when an RFID card is read.

The RFID information is saved in the badge data structure until the device
completes a cycle. After a cycle is complete, the badge details are reset to
the default values


"""
def handle_RFID_scan():
    global data_RFID
    global badge
    badge = Badge(pcprox._format_hex(data_RFID[0]), "JOHN DOE")
    


"""
_idle

Called when in the IDLE state.

"""
def _idle():
    global card_reader
    global data_RFID, data_RFID_prev

    # Scan for RFIDs forever
    data_RFID_prev = data_RFID
    data_RFID = card_reader.scan()
    
    # See if we actually read a new RFID
    new_tag_read = (data_RFID_prev != data_RFID)
    if new_tag_read and (data_RFID is not None):
        print('Tag data: %s' % pcprox._format_hex(data_RFID[0]))
        print('Bit length: %d' % data_RFID[1])
        handle_RFID_scan()



"""
_disinfecting

Called when in the DISINFECTING state.

"""
def _disinfecting():
    pass


"""
_check_door_leds

Called ALWAYS.

This function checks the state of the device using the corresponding GPIO pin
and sets the "device active" variable based on the HIGH or LOW state.

"""
def _check_device_status():
    global device_active
    if GPIO.input(PIN_DEVICE) == GPIO.LOW:
        device_active = True
    else:
        device_active = False


"""
_check_door_leds

Called while in the DISINFECTING state.

This function reads the states of the GPIO pins associated with the DOOR LEDs 
and compares them to the previous states. If there is a change in state, the
time of START or END is set using the get_current_time() function.


"""
def _check_door_leds():
    global time_door_red_led, time_door_green_led
    global state_door_green_led, state_door_green_led_prev
    global state_door_red_led, state_door_red_led_prev
    
    state_door_red_led_prev = state_door_red_led
    state_door_red_led = GPIO.input(PIN_DOOR_RED_LED)
    need_transition_red = (state_door_red_led != state_door_red_led_prev)
    if need_transition_red:
        if state_door_red_led == GPIO.LOW:
            time_door_red_led[0] = get_current_time()
        else:
            time_door_red_led[1] = get_current_time()
        
    state_door_green_led_prev = state_door_green_led
    state_door_green_led = GPIO.input(PIN_DOOR_GREEN_LED)
    need_transition_green = (state_door_green_led != state_door_green_led_prev)
    if need_transition_green:
        if state_door_green_led == GPIO.LOW:
            time_door_green_led[0] = get_current_time()
        else:
            time_door_green_led[1] = get_current_time()
            

"""
_check_uv_leds

Called while in the DISINFECTING state.

This function reads the state of the GPIO pin associated with the UV LEDs 
and compares it to the previous state. If there is a change in state, the
time of START or END is set using the get_current_time() function.


"""
def _check_uv_leds():
    global time_uv_leds
    global state_uv_leds, state_uv_leds_prev
    
    state_uv_leds = GPIO.input(PIN_UV_LED)
    need_transition = (state_uv_leds != state_uv_leds_prev)
    if need_transition:
        state_uv_leds_prev = state_uv_leds
        if state_uv_leds == GPIO.LOW:
            time_uv_leds[0] = get_current_time()
            #print("UV LEDs ON")
        else:
            time_uv_leds[1] = get_current_time()
            #print("UV LEDs OFF")


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
    
    leds_turned_on = (time_uv_leds[0] != None)
    leds_turned_off = (time_uv_leds[1] != None) 
    if leds_turned_on and leds_turned_off:
        impossibly_early = (time_uv_leds[1] < time_uv_leds[0])
        impossibly_exact = (time_uv_leds[1] == time_uv_leds[0]) 
        impossible_time = impossibly_exact or impossibly_early
        if impossible_time:
            # The LEDs must have shut off at the same time as the device.
            time_uv_leds[1] = get_current_time()
    else:
        time_uv_leds[1] = None
        
    


"""
clear_report_details

Clears the details of the report for the next cycle.
"""
def clear_report_details():
    global badge
    global time_device_active
    global time_uv_leds
    global time_door_green_led
    global time_door_red_led
    badge = Badge()
    time_device_active = [None, None]
    time_uv_leds = [None, None]
    time_door_green_led = [None, None]
    time_door_red_led = [None, None]


"""
is_cycle_complete

Tells if a cycle was complete based on the duration (~26 seconds).
Placeholder. 

"""
def is_complete_cycle(duration):
    if duration >= CYCLE_TIME_EXPECTED:
        return True
    else:
        return False


"""
create_report

Creates a report with the badge ID, the time ON/OFF for all  LEDs and 
any other information required.


Report fields (Rev. Jan 16, 2025):
    badge
    time_device_active
    time_uv_leds
    time_door_green_led
    time_door_red_led

"""
def create_report():
    global badge
    global time_device_active
    global time_uv_leds
    global time_door_green_led
    global time_door_red_led
    
    # Get the report date (the cycle start time)
    report_date = time_device_active[0]
    
    # Get the cycle duration (duration of timer relay ON to timer relay OFF)
    cycle_duration = 0
    if not (None in time_device_active):
        cycle_duration = (time_device_active[1] - time_device_active[0]).total_seconds()
    complete_cycle = is_complete_cycle(cycle_duration)
    
    # Get the UV duration
    uv_duration = 0
    if not (None in time_uv_leds):
        uv_duration = (time_uv_leds[1] - time_uv_leds[0]).total_seconds()
    
        
    report = '************************************************\n'
    report += f"REPORT\n"
    report += f"  Date: {report_date}\n"
    report += f"  Badge ID Read: {badge.scanned}\n"
    report += f"  Badge ID Number: {badge.number}\n"
    report += f"  Name: {badge.name}\n"
    #report += '************************************************\n'
    report += f"  UV LEDs ON: {time_uv_leds[0]}\n"
    report += f"  UV LEDs OFF: {time_uv_leds[1]}\n"
    report += f"  Door Green LED ON: {time_door_green_led[0]}\n"
    report += f"  Door Green LED OFF: {time_door_green_led[1]}\n"
    report += f"  Door Red LED ON: {time_door_red_led[0]}\n"
    report += f"  Door Red LED OFF: {time_door_red_led[1]}\n"
    #report += '************************************************\n'
    report += f"  UV duration: {uv_duration}\n"
    report += f"  Cycle duration: {cycle_duration}\n"
    report += f"  Cycle complete: {complete_cycle}\n"
    report += '************************************************\n'
    
    uv_led_status = get_diagnostic_uv_leds(time_uv_leds,cycle_duration)
    door_green_led_status = get_diagnostic_door_leds(time_door_green_led,cycle_duration)
    door_red_led_status = get_diagnostic_door_leds(time_door_red_led,cycle_duration)
    report += f"HARDWARE ASSESSMENT\n"
    report += f"  UV LED: {uv_led_status}\n"
    report += f"  Door Green LED: {door_green_led_status}\n"
    report += f"  Door Red LED: {door_red_led_status} \n\n"
    return report




"""
get_diagnostic_uv_leds

<<NOT READY FOR PRODUCTION>>

An EXAMPLE function to demonstrate an onboard diagnostic based on LED times.
Returns a string with an appropriate error message.

Note, this function is VERY similar to 'get_diagnostic_door_leds' but it 
differs in the time it checks because the UV LEDs have a delay with respect
to the device.

"""
def get_diagnostic_uv_leds(time_on_off,cycle_time):
    uv_leds_dead = (time_on_off[1] == None and time_on_off[0] == None)
    if uv_leds_dead:
        return 'CRITICAL. LEDs NOT DETECTED. REPLACE LEDs OR SENSOR.'
    
    uv_led_status = ''
    if None in time_on_off:
        return 'WARNING. INVALID TIME RANGE. CHECK LEDs OR SENSOR.'
    
    uv_duration = (time_on_off[1] - time_on_off[0]).total_seconds()
    short_cycle = (uv_duration < CYCLE_TIME_EXPECTED) and (uv_duration < cycle_time - 1.5)
    if short_cycle:
        return 'WARNING. LEDs TURNED OFF PREMATURELY.'
    else:
        return 'OK.'


"""
get_diagnostic_door_leds

<<NOT READY FOR PRODUCTION>>

An EXAMPLE function to demonstrate an onboard diagnostic based on LED times.
Returns a string with an appropriate error message.

"""
def get_diagnostic_door_leds(time_on_off,cycle_time):
    leds_dead = (time_on_off[1] == None and time_on_off[0] == None)
    if leds_dead:
        return 'CRITICAL. LEDs NOT DETECTED. REPLACE LEDs OR SENSOR.'
    
    led_status = ''
    if None in time_on_off:
        return 'WARNING. INVALID TIME. CHECK LEDs OR SENSOR.'
        
    duration = abs((time_on_off[1] - time_on_off[0]).total_seconds())
    short_cycle = (duration < CYCLE_TIME_EXPECTED) and (duration < cycle_time)
    if short_cycle:
        return 'WARNING. LEDs TURNED OFF PREMATURELY'
    else:
        return 'OK.'
    
    return led_status
    

"""
get_current_time_iso

Returns the current time in the ISO-8601 format.

"""
def get_current_time_iso():
    return datetime.now().replace(microsecond=0).isoformat()


"""
get_current_time

Returns the current time in the default format.

"""
def get_current_time():
    return datetime.now().replace(microsecond=0)


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


if __name__ == '__main__':
    main()
