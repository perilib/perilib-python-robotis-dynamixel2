import struct
import perilib

from .RobotisDynamixel2Protocol import *

class RobotisDynamixel2ParserGenerator(perilib.StreamParserGenerator):

    def __init__(self, protocol_class=RobotisDynamixel2Protocol, stream=None):
        super().__init__(protocol_class, stream)
        self.last_instruction = None

    def _on_tx_packet(self, packet):
        # store instruction byte for reference
        self.last_instruction = packet.buffer[7]
        super()._on_tx_packet(packet)
