# check for local development repo in script path and use it for imports
import os, sys
path_parts = os.path.dirname(os.path.realpath(__file__)).split(os.sep)
if "perilib-python-core" in path_parts:
    sys.path.insert(0, os.sep.join(path_parts[:-path_parts[::-1].index("perilib-python-core")]))

import time
import perilib
import perilib.robotis_dynamixel2

class App():

    def __init__(self):
        # set up protocol parser (handles imcoming data and builds outgoing data)
        self.parser_generator = perilib.robotis_dynamixel2.RobotisDynamixel2ParserGenerator(protocol_class=perilib.robotis_dynamixel2.RobotisDynamixel2Protocol)
        self.parser_generator.on_rx_packet = self.on_rx_packet
        self.parser_generator.on_rx_error = self.on_rx_error

    def on_rx_packet(self, packet):
        print("[%.03f] RXP: %s" % (time.time(), packet))

    def on_rx_error(self, e, rx_buffer, parser_generator):
        print("[%.03f] ERROR: %s (raw data: [%s] via %s)" % (time.time(), e, ' '.join(["%02X" % b for b in rx_buffer]), parser_generator))
        
def main():
    app = App()
    
    # manually emulate a ping instruction
    app.parser_generator.last_instruction = 0x01
    
    # parse() data with list of integers forming status packet
    app.parser_generator.parse([0xFF, 0xFF, 0xFD, 0x00, 0x01, 0x07, 0x00, 0x55, 0x00, 0x06, 0x04, 0x26, 0x65, 0x5D])
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Ctrl+C detected, terminating script")
        sys.exit(0)
