import struct
import perilib

from .RobotisDynamixel2Packet import *

class RobotisDynamixel2Protocol(perilib.StreamProtocol):

    # http://emanual.robotis.com/docs/en/dxl/protocol2/

    header_args = [
        { "name": "sof1", "type": "uint8" },
        { "name": "sof2", "type": "uint8" },
        { "name": "sof3", "type": "uint8" },
        { "name": "reserved", "type": "uint8" },
        { "name": "packet_id", "type": "uint8" },
        { "name": "packet_length", "type": "uint16" },
        { "name": "instruction", "type": "uint8" }
    ]

    footer_args = [
        { "name": "crc", "type": "uint16" }
    ]

    incoming_packet_timeout = 0.25
    response_packet_timeout = 0.25
    
    instructions = {
        0x01: { # id = 0x01 (ping)
            "name": "ping",
            "outgoing_args": [],
            "incoming_args": [
                { "name": "error", "type": "uint8" },
                { "name": "model_number", "type": "uint16" },
                { "name": "firmware_version", "type": "uint8" }
            ],
        },
        0x02: { # id = 0x02 (read)
            "name": "read",
            "outgoing_args": [
                { "name": "address", "type": "uint16" },
                { "name": "length", "type": "uint16" }
            ],
            "incoming_args": [
                { "name": "error", "type": "uint8" },
                { "name": "data", "type": "uint8a-greedy" }
            ],
        },
        0x03: { # id = 0x03 (write)
            "name": "write",
            "outgoing_args": [
                { "name": "address", "type": "uint16" },
                { "name": "data", "type": "uint8a-greedy" }
            ],
            "incoming_args": [
                { "name": "error", "type": "uint8" }
            ],
        },
        0x04: { # id = 0x04 (reg_write)
            "name": "reg_write",
            "outgoing_args": [
                { "name": "address", "type": "uint16" },
                { "name": "data", "type": "uint8a-greedy" }
            ],
            "incoming_args": [
                { "name": "error", "type": "uint8" }
            ],
        },
        0x05: { # id = 0x05 (action)
            "name": "action",
            "outgoing_args": [],
            "incoming_args": [
                { "name": "error", "type": "uint8" }
            ],
        },
        0x06: { # id = 0x06 (factory_reset)
            "name": "factory_reset",
            "outgoing_args": [
                { "name": "type", "type": "uint8" }
            ],
            "incoming_args": [
                { "name": "error", "type": "uint8" }
            ],
        },
        0x08: { # id = 0x08 (reboot)
            "name": "reboot",
            "outgoing_args": [],
            "incoming_args": [
                { "name": "error", "type": "uint8" }
            ],
        },
        0x10: { # id = 0x10 (clear)
            "name": "clear",
            "outgoing_args": [
                { "name": "type", "type": "uint8" },
                { "name": "code", "type": "uint32" }
            ],
            "incoming_args": [
                { "name": "error", "type": "uint8" }
            ],
        },
        0x82: { # id = 0x82 (sync_read)
            "name": "sync_read",
            "outgoing_args": [
                { "name": "address", "type": "uint16" },
                { "name": "length", "type": "uint16" },
                { "name": "id_list", "type": "uint8a-greedy" }
            ],
            "incoming_args": [
                { "name": "error", "type": "uint8" },
                { "name": "data", "type": "uint8a-greedy" }
            ],
        },
        0x83: { # id = 0x83 (sync_write)
            "name": "sync_write",
            "outgoing_args": [
                { "name": "address", "type": "uint16" },
                { "name": "length", "type": "uint16" },
                { "name": "id_data_list", "type": "uint8a-greedy" }
            ],
            "incoming_args": [],
        },
        0x92: { # id = 0x92 (bulk_read)
            "name": "bulk_read",
            "outgoing_args": [
                { "name": "id_address_length_list", "type": "uint8a-greedy" }
            ],
            "incoming_args": [
                { "name": "error", "type": "uint8" },
                { "name": "data", "type": "uint8a-greedy" }
            ],
        },
        0x93: { # id = 0x93 (bulk_write)
            "name": "sync_write",
            "outgoing_args": [
                { "name": "id_address_length_data_list", "type": "uint8a-greedy" }
            ],
            "incoming_args": [],
        },
    }

    @classmethod
    def test_packet_start(cls, buffer, is_tx=False):
        if len(buffer) == 1 and buffer[0] == 0xFF: return perilib.ParseStatus.STARTING
        if len(buffer) == 2 and buffer[1] == 0xFF: return perilib.ParseStatus.STARTING
        if len(buffer) == 3 and buffer[2] == 0xFD: return perilib.ParseStatus.IN_PROGRESS
        return perilib.ParseStatus.IDLE

    @classmethod
    def test_packet_complete(cls, buffer, is_tx=False):
        # make sure we have at least up to the packet length field
        if len(buffer) >= 7:
            # check 11-bit "length" field in 4-byte header
            (packet_length,) = struct.unpack("<H", buffer[5:7])
            if len(buffer) == packet_length + 7:
                (crc,) = struct.unpack("<H", buffer[-2:])
                return perilib.ParseStatus.COMPLETE

        # not finished if we made it here
        return perilib.ParseStatus.IN_PROGRESS

    @classmethod
    def get_packet_from_buffer(cls, buffer, parser_generator=None, is_tx=False):
        (id, length, instruction) = struct.unpack("<BHB", buffer[4:8])
        (crc,) = struct.unpack("<H", buffer[-2:])
        
        # remove byte stuffing from instruction/payload, if present
        unstuffed_buffer = []
        unstuffing_needed = False
        seen = []
        for b in buffer[8:-2]:
            unstuff_this_byte = False
            if b == 0xFF and len(seen) == 0:
                seen.append(b)
            elif b == 0xFF and len(seen) == 1:
                seen.append(b)
            elif b == 0xFD and len(seen) == 2:
                # stuff an extra 0xFD byte and reset status
                unstuffing_needed = True
                unstuff_this_byte = True
                seen = []
            else:
                # pattern broken, reset
                seen = []
                
            if not unstuff_this_byte:
                unstuffed_buffer.append(b)
                
        # add the CRC field at the end (not checked for stuffing)
        for b in buffer[-2:]:
            unstuffed_buffer.append(b)
                
        # replace original buffer with unstuffed one
        if unstuffing_needed:
            buffer = bytes(unstuffed_buffer)
        
        try:
            if instruction == 0x55:
                if "last_instruction" in parser_generator.__dict__:
                    packet_type = RobotisDynamixel2Packet.TYPE_STATUS
                    packet_definition = RobotisDynamixel2Protocol.instructions[parser_generator.last_instruction]
                    packet_name = "stat_%s" % packet_definition["name"]
                else:
                    raise perilib.PerilibProtocolException(
                            "No known previous instruction, cannot match status packet with correct definition")
            else:
                packet_type = RobotisDynamixel2Packet.TYPE_INSTRUCTION
                packet_definition = RobotisDynamixel2Protocol.instructions[instruction]
                if len(packet_definition["incoming_args"]) > 0:
                    packet_definition["response_required"] = "stat_%s" % packet_definition["name"]
                packet_name = "inst_%s" % packet_definition["name"]
                parser_generator.last_instruction = instruction
        except KeyError as e:
            raise perilib.PerilibProtocolException(
                    "Could not find packet definition for instruction 0x%02X"
                    % (parser_generator.last_instruction))

        packet_definition["header_args"] = RobotisDynamixel2Protocol.header_args
        packet_definition["footer_args"] = RobotisDynamixel2Protocol.footer_args
        packet_metadata = {
            "id": id,
            "instruction": instruction,
            "crc": crc
        }

        return RobotisDynamixel2Packet(type=packet_type, name=packet_name, definition=packet_definition, buffer=buffer, metadata=packet_metadata, parser_generator=parser_generator)

    @classmethod
    def get_packet_from_name_and_args(cls, _packet_name, _parser_generator=None, **kwargs):
        # prepend instruction slug if no slug present
        if len(_packet_name) < 6 or _packet_name[0:5] not in ["inst_", "stat_"]:
            _packet_name = "inst_" + _packet_name
            
        # split "ble_cmd_system_hello" into relevant parts
        parts = _packet_name.split('_', maxsplit=1)
        instruction_name = parts[1]
        if parts[0] == "inst":
            # outgoing instruction
            packet_type = RobotisDynamixel2Packet.TYPE_INSTRUCTION
        elif parts[0] == "stat":
            # incoming status packet
            packet_type = RobotisDynamixel2Packet.TYPE_STATUS

        # find the entry in the protocol definition table
        for instruction in RobotisDynamixel2Protocol.instructions:
            if type(instruction) == str:
                continue
            if RobotisDynamixel2Protocol.instructions[instruction]["name"] == instruction_name:
                packet_definition = RobotisDynamixel2Protocol.instructions[instruction]
                packet_definition["header_args"] = RobotisDynamixel2Protocol.header_args
                packet_definition["footer_args"] = RobotisDynamixel2Protocol.footer_args
                if len(packet_definition["incoming_args"]) > 0:
                    packet_definition["response_required"] = "stat_%s" % packet_definition["name"]

                packet_metadata = {
                    "id": kwargs["id"],
                    "instruction": instruction,
                    "crc": None
                }
                
                return RobotisDynamixel2Packet(type=packet_type, name=_packet_name, definition=packet_definition, payload=kwargs, metadata=packet_metadata, parser_generator=_parser_generator)

        # unable to find correct packet
        raise perilib.PerilibProtocolException("Unable to locate packet definition for '%s'" % _packet_name)
