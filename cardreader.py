"""
File: 

    cardreader.py

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
    def __init__(self):
        self.dev = pcprox.open_pcprox(debug=False)

        # Show the device info
        #print(repr(dev.get_device_info()))

        # Dump the configuration from the device.
        self.config = self.dev.get_config()
        self.config.print_config()

        # Disable sending keystrokes and update config
        self.config.bHaltKBSnd = True
        self.config.set_config(self.dev)
        self.dev.end_config()

        sleep(.5)


    def scan_for_tags(self):
        return self.dev.get_tag()


    def __del__(self):
        self.config.bHaltKBSnd = True
        self.config.set_config(self.dev)
        self.dev.end_config()
        
