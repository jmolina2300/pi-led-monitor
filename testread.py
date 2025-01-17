#!/usr/bin/env python3
#
# This script tests the pcprox module on its own.
#
#
import pcprox
from time import sleep


def main(debug=False):
    dev = pcprox.open_pcprox(debug=debug)

    # Show the device info
    print(repr(dev.get_device_info()))

    # Dump the configuration from the device.
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
            deal_with_tag
        
        sleep(1)



    # Restore configuration
    config.bHaltKBSnd = True
    config.set_config(dev)
    dev.end_config()


def deal_with_tag():
    pass


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Test program for pcprox which reads a card in the field')

    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug traces')

    options = parser.parse_args()
    main(options.debug)
