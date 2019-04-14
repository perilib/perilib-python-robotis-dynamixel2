import struct
import perilib

from .RobotisDynamixel2Packet import *

class RobotisDynamixel2Protocol(perilib.StreamProtocol):

    # http://emanual.robotis.com/docs/en/dxl/protocol2/

    crc_table = [
        0x0000, 0x8005, 0x800F, 0x000A, 0x801B, 0x001E, 0x0014, 0x8011,
        0x8033, 0x0036, 0x003C, 0x8039, 0x0028, 0x802D, 0x8027, 0x0022,
        0x8063, 0x0066, 0x006C, 0x8069, 0x0078, 0x807D, 0x8077, 0x0072,
        0x0050, 0x8055, 0x805F, 0x005A, 0x804B, 0x004E, 0x0044, 0x8041,
        0x80C3, 0x00C6, 0x00CC, 0x80C9, 0x00D8, 0x80DD, 0x80D7, 0x00D2,
        0x00F0, 0x80F5, 0x80FF, 0x00FA, 0x80EB, 0x00EE, 0x00E4, 0x80E1,
        0x00A0, 0x80A5, 0x80AF, 0x00AA, 0x80BB, 0x00BE, 0x00B4, 0x80B1,
        0x8093, 0x0096, 0x009C, 0x8099, 0x0088, 0x808D, 0x8087, 0x0082,
        0x8183, 0x0186, 0x018C, 0x8189, 0x0198, 0x819D, 0x8197, 0x0192,
        0x01B0, 0x81B5, 0x81BF, 0x01BA, 0x81AB, 0x01AE, 0x01A4, 0x81A1,
        0x01E0, 0x81E5, 0x81EF, 0x01EA, 0x81FB, 0x01FE, 0x01F4, 0x81F1,
        0x81D3, 0x01D6, 0x01DC, 0x81D9, 0x01C8, 0x81CD, 0x81C7, 0x01C2,
        0x0140, 0x8145, 0x814F, 0x014A, 0x815B, 0x015E, 0x0154, 0x8151,
        0x8173, 0x0176, 0x017C, 0x8179, 0x0168, 0x816D, 0x8167, 0x0162,
        0x8123, 0x0126, 0x012C, 0x8129, 0x0138, 0x813D, 0x8137, 0x0132,
        0x0110, 0x8115, 0x811F, 0x011A, 0x810B, 0x010E, 0x0104, 0x8101,
        0x8303, 0x0306, 0x030C, 0x8309, 0x0318, 0x831D, 0x8317, 0x0312,
        0x0330, 0x8335, 0x833F, 0x033A, 0x832B, 0x032E, 0x0324, 0x8321,
        0x0360, 0x8365, 0x836F, 0x036A, 0x837B, 0x037E, 0x0374, 0x8371,
        0x8353, 0x0356, 0x035C, 0x8359, 0x0348, 0x834D, 0x8347, 0x0342,
        0x03C0, 0x83C5, 0x83CF, 0x03CA, 0x83DB, 0x03DE, 0x03D4, 0x83D1,
        0x83F3, 0x03F6, 0x03FC, 0x83F9, 0x03E8, 0x83ED, 0x83E7, 0x03E2,
        0x83A3, 0x03A6, 0x03AC, 0x83A9, 0x03B8, 0x83BD, 0x83B7, 0x03B2,
        0x0390, 0x8395, 0x839F, 0x039A, 0x838B, 0x038E, 0x0384, 0x8381,
        0x0280, 0x8285, 0x828F, 0x028A, 0x829B, 0x029E, 0x0294, 0x8291,
        0x82B3, 0x02B6, 0x02BC, 0x82B9, 0x02A8, 0x82AD, 0x82A7, 0x02A2,
        0x82E3, 0x02E6, 0x02EC, 0x82E9, 0x02F8, 0x82FD, 0x82F7, 0x02F2,
        0x02D0, 0x82D5, 0x82DF, 0x02DA, 0x82CB, 0x02CE, 0x02C4, 0x82C1,
        0x8243, 0x0246, 0x024C, 0x8249, 0x0258, 0x825D, 0x8257, 0x0252,
        0x0270, 0x8275, 0x827F, 0x027A, 0x826B, 0x026E, 0x0264, 0x8261,
        0x0220, 0x8225, 0x822F, 0x022A, 0x823B, 0x023E, 0x0234, 0x8231,
        0x8213, 0x0216, 0x021C, 0x8219, 0x0208, 0x820D, 0x8207, 0x0202
    ]
    
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
    def test_packet_start(cls, buffer, new_byte, is_tx=False):
        if len(buffer) == 0 and new_byte == 0xFF: return perilib.ParseStatus.STARTING
        if len(buffer) == 1 and new_byte == 0xFF: return perilib.ParseStatus.STARTING
        if len(buffer) == 2 and new_byte == 0xFD: return perilib.ParseStatus.IN_PROGRESS
        return perilib.ParseStatus.IDLE

    @classmethod
    def test_packet_complete(cls, buffer, new_byte, is_tx=False):
        # make sure we have at least up to the packet length field
        temp_buffer = buffer + bytes([new_byte])
        if len(temp_buffer) >= 7:
            # check 11-bit "length" field in 4-byte header
            (packet_length,) = struct.unpack("<H", temp_buffer[5:7])
            if len(temp_buffer) == packet_length + 7:
                (crc,) = struct.unpack("<H", temp_buffer[-2:])
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
