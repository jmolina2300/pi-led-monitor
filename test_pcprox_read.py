#!/usr/bin/env python3
#
# This script tests the pcprox module on its own.
#
# Run with ./test_pcprox_read
#
# OR with ./test_pcprox_read -d
#
import pcprox
from time import sleep


def main(debug=False):

    # Instantiate device
    dev = pcprox.open_pcprox(debug=debug)

    # (Optional) Show the device info
    print(repr(dev.get_device_info()))

    # (Optional) Dump the configuration from the device 
    config = dev.get_config()
    config.print_config()

    # Disable sending keystrokes and update config
    config.bHaltKBSnd = True
    config.set_config(dev)

    # Exit configuration mode
    dev.end_config()

    # Wait half a second
    sleep(.5)

    
    print('Waiting for a card...')
    while True:
        
        # Get the tag
        found_card = False
        tag = dev.get_tag()
        
        if tag is not None:
            found_card = True

            # Print the tag ID on screen
            print('Tag data: %s' % pcprox._format_hex(tag[0]))
            print('Bit length: %d' % tag[1])
        
        sleep(1)



    # Restore configuration
    config.bHaltKBSnd = True
    config.set_config(dev)
    dev.end_config()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Test program for pcprox which reads a card in the field')

    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug traces')

    options = parser.parse_args()
    main(options.debug)
