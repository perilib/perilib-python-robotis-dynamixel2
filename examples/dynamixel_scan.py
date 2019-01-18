# check for local development repo in script path and use it for imports
import os, sys
path_parts = os.path.dirname(os.path.realpath(__file__)).split(os.sep)
if "perilib-python-core" in path_parts:
    sys.path.insert(0, os.sep.join(path_parts[:-path_parts[::-1].index("perilib-python-core")]))

import time
import perilib
import perilib.protocol.stream.robotis_dynamixel2

class App():

    def __init__(self):
        # device instance (assigned to SerialDevice derived class when stream opens)
        self.dxl = None
        
        # set up manager (detects USB insertion/removal, creates data stream and parser/generator instances as needed)
        self.manager = perilib.hal.serial.SerialManager(
            device_class=perilib.protocol.stream.robotis_dynamixel2.RobotisDynamixel2Device,
            stream_class=perilib.hal.serial.SerialStream,
            parser_generator_class=perilib.protocol.stream.robotis_dynamixel2.RobotisDynamixel2ParserGenerator,
            protocol_class=perilib.protocol.stream.robotis_dynamixel2.RobotisDynamixel2Protocol)
        self.manager.device_filter = lambda device: device.port_info.vid == 0xFFF1 and device.port_info.pid == 0xFF48
        self.manager.on_connect_device = self.on_connect_device         # triggered by manager when running
        self.manager.on_disconnect_device = self.on_disconnect_device   # triggered by manager when running (if stream is closed) or stream (if stream is open)
        self.manager.on_open_stream = self.on_open_stream               # triggered by stream
        self.manager.on_close_stream = self.on_close_stream             # triggered by stream
        #self.manager.on_rx_data = self.on_rx_data                       # triggered by stream
        #self.manager.on_tx_data = self.on_tx_data                       # triggered by stream
        #self.manager.on_rx_packet = self.on_rx_packet                   # triggered by parser/generator
        #self.manager.on_tx_packet = self.on_tx_packet                   # triggered by parser/generator
        self.manager.on_rx_error = self.on_rx_error                     # triggered by parser/generator
        #self.manager.on_incoming_packet_timeout = self.on_incoming_packet_timeout   # triggered by parser/generator
        #self.manager.on_response_packet_timeout = self.on_response_packet_timeout   # triggered by parser/generator
        self.manager.auto_open = perilib.hal.serial.SerialManager.AUTO_OPEN_SINGLE
        
        # start monitoring for devices
        self.manager.start()

    def on_connect_device(self, device):
        print("[%.03f] CONNECTED: %s" % (time.time(), device))

    def on_disconnect_device(self, device):
        print("[%.03f] DISCONNECTED: %s" % (time.time(), device))

    def on_open_stream(self, stream):
        print("[%.03f] OPENED: %s" % (time.time(), stream))

        # store Dynamixel bus device and attach relevant stream management functions to it
        # (NOTE: this behavior is specific to the RobotisDynamixel2Device class)
        self.dxl = stream.device
        self.dxl.attach_stream(stream)

    def on_close_stream(self, stream):
        print("[%.03f] CLOSED: %s" % (time.time(), stream))
        self.dxl = None

    def on_rx_data(self, data, stream):
        print("[%.03f] RXD: [%s] via %s" % (time.time(), ' '.join(["%02X" % b for b in data]), stream))

    def on_tx_data(self, data, stream):
        print("[%.03f] TXD: [%s] via %s" % (time.time(), ' '.join(["%02X" % b for b in data]), stream))

    def on_rx_packet(self, packet):
        print("[%.03f] RXP: %s" % (time.time(), packet))

    def on_tx_packet(self, packet):
        print("[%.03f] TXP: %s" % (time.time(), packet))

    def on_rx_error(self, e, rx_buffer, parser_generator):
        print("[%.03f] ERROR: %s (raw data: [%s] via %s)" % (time.time(), e, ' '.join(["%02X" % b for b in rx_buffer]), parser_generator))

    def on_incoming_packet_timeout(self, rx_buffer, parser_generator):
        print("[%.03f] RXP TIMEOUT: partial packet data: [%s] via %s" % (time.time(), ' '.join(["%02X" % b for b in rx_buffer]), parser_generator))
        
    def on_response_packet_timeout(self, waiting_for, parser_generator):
        print("[%.03f] RSP TIMEOUT: waiting for %s via %s" % (time.time(), waiting_for, parser_generator))
        
def main():
    app = App()
    while True:
        # wait for the USB serial device to connect
        if app.dxl is not None:
            if not app.dxl.is_scanned:
                # query servos on the bus
                print("Dynamixel servo bus connected, scanning for servos...")
                app.dxl.scan()
                
                # show list of attached servos
                print("Found %d servo(s)" % len(app.dxl.servos))
                [print(" - %s" % servo) for id, servo in app.dxl.servos.items()]
                
                # read control tables for each
                print("Reading control tables for attached servos")
                for id, servo in app.dxl.servos.items():
                    servo.read_control_table()
                    print("Servo #%d" % id)
                    print("  - operating_mode: %d" % servo.control_table.operating_mode)
                    print("  - present_position: %d" % servo.control_table.present_position)
                    print("  - present_velocity: %d" % servo.control_table.present_velocity)
                    
        time.sleep(0.05)

if __name__ == '__main__':
    main()
