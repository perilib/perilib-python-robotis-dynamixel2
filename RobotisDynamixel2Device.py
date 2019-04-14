import perilib

from .RobotisDynamixel2Servo import *

class RobotisDynamixel2Device(perilib.StreamDevice):
    
    def __init__(self, id, port):
        super().__init__(id, port)
        self.is_scanned = False
        self.servos = {}
    
    def attach_stream(self, stream):
        stream.parser_generator.on_rx_packet = self.on_rx_packet
    
    def on_rx_packet(self, packet):
        if packet.name == "stat_ping":
            # add servo to internal list if not already present
            if packet.metadata["id"] not in self.servos:
                self.servos[packet.metadata["id"]] = Servo(
                        id=packet.metadata["id"],
                        model_number=packet["model_number"],
                        firmware_version=packet["firmware_version"],
                        device=self)

    def broadcast_packet(self, _packet_name, **kwargs):
        return self.stream.parser_generator.send_packet(_packet_name, id=0xFE, **kwargs)
        
    def wait_packet(self, _packet_name=None):
        return self.stream.parser_generator.wait_packet(_packet_name)
       
    def scan(self):
        # send ping instruction to entire bus
        self.broadcast_packet("inst_ping")
        
        # wait for ping status replies until we time out
        while self.wait_packet("stat_ping") is not None: pass
        
        # mark as scanned and return servo count
        self.is_scanned = True
        return len(self.servos)
