"""
File: 

    cardreader.py

WARNING:

    This code is not ready for production. It is a very simple wrapper that
    was created to simplify the code in main.py. More work will need to be 
    done on the pcprox module directly to avoid fatal crashes.
    
    For example, if the card reader is unplugged when this module is used, 
    the script will throw an error and stop.
    
    Look at the 'test_pcprox_read.py' example code and the 'pcprox.py' module
    to see how everything works at the lowest level.

Description:
    
    This file contains a CardReader class that encapsulates the 
    implementation-specific details for a card reading device. In this 
    case, it is a PC Prox RDR-6082AKU card reader connected via USB. 
    This class uses an open-source pcprox module to control it.
    
    For future reference, this is perhaps how we could add support for
    different card readers; a new class could be defined for each type
    and at startup, the specific device could be identified and the 
    appropriate Class would be instantiated.
    

"""

from time import sleep
import pcprox


class CardReader:
    def __init__(self, debug):
        self.dev = pcprox.open_pcprox(debug=debug)

        # Show the device info
        #print(repr(dev.get_device_info()))

        # Get the device configuration
        self.config = self.dev.get_config()
        
        # Dump the configuration from the device if debug enabled
        if debug:
            self.config.print_config()

        # Disable sending keystrokes and update config
        self.config.bHaltKBSnd = True
        self.config.set_config(self.dev)
        self.dev.end_config()

        sleep(.5)


    def scan(self):
        return self.dev.get_tag()


    def __del__(self):
        self.config.bHaltKBSnd = True
        self.config.set_config(self.dev)
        self.dev.end_config()
        
