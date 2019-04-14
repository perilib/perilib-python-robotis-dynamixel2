import struct
import perilib

from .RobotisDynamixel2Protocol import *

class RobotisDynamixel2Packet(perilib.StreamPacket):

    TYPE_INSTRUCTION = 0
    TYPE_STATUS = 1

    TYPE_STR = ["instruction", "status"]
    TYPE_ARG_CONTEXT = ["outgoing_args", "incoming_args"]

    def prepare_buffer_after_building(self):
        # perform byte stuffing on payload
        stuffed_buffer = []
        stuffing_needed = False
        seen = [self.metadata["instruction"]]
        for b in self.buffer:
            stuffed_buffer.append(b)
            if b == 0xFF and len(seen) == 0:
                seen.append(b)
            elif b == 0xFF and len(seen) == 1:
                seen.append(b)
            elif b == 0xFD and len(seen) == 2:
                # stuff an extra 0xFD byte and reset status
                stuffing_needed = True
                stuffed_buffer.append(0xFD)
                seen = []
            else:
                # pattern broken, reset
                seen = []
                
        # replace original buffer with stuffed one
        if stuffing_needed:
            self.buffer = bytes(stuffed_buffer)

        # build header (SOF, servo ID, length, and instruction data)
        header = struct.pack("<5BHB",
            0xFF, 0xFF, 0xFD, 0x00,
            self.metadata["id"], len(self.buffer) + 3, self.metadata["instruction"])

        # prepend header to buffer
        self.buffer = header + self.buffer
        
        # calculate CRC16-IBM and build footer (CRC16 IBM mechanism)
        self.metadata["crc"] = self.update_crc(0, self.buffer)
        self.buffer = self.buffer + struct.pack("<H", self.metadata["crc"])
        
    def update_crc(self, crc_accum, data_blk):
        for b in data_blk:
            i = ((crc_accum >> 8) ^ b) & 0xFF
            crc_accum = ((crc_accum << 8) ^ RobotisDynamixel2Protocol.crc_table[i]) & 0xFFFF
        return crc_accum
