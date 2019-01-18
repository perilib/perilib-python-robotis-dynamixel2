import perilib

class ControlTable():
    
    size = 0
    fields = []
    
    def __init__(self, buffer=None):
        if buffer is not None:
            # create dictionary from buffer
            self.populate_data_from_buffer(buffer)
        else:
            # create empty table for replacement or selective updates later
            self._data = {}
            for field in self.fields:
                self._data[field["name"]] = None

    def __getitem__(self, arg):
        return self._data[arg]
    
    def __getattr__(self, arg):
        if arg in self.__dict__:
            return self.__dict__[arg]
        else:
            return self._data[arg]
    
    def __str__(self):
        lines = []
        for field in self.fields:
            if "___" not in field["name"]:
                if self._data[field["name"]] is None:
                    lines.append("%22s: None" % (field["name"]))
                else:
                    lines.append("%22s: %d" % (field["name"], self._data[field["name"]]))
        return '\n'.join(lines)
        
    def populate_data_from_buffer(self, buffer):
        self._data = perilib.protocol.Protocol.unpack_values(buffer, self.fields)
        
    def get_field_info(self, field_name):
        for field in self.fields:
            if field["name"] == field_name:
                return field
        return None
        
class ControlTableX(ControlTable):
    
    size = 147
    fields = [
        # EEPROM
        { "eeprom": 1,  "name": "model_number",             "type": "uint16",                       "address": 0,       "writable": 0 },
        { "eeprom": 1,  "name": "model_information",        "type": "uint32",                       "address": 2,       "writable": 0 },
        { "eeprom": 1,  "name": "firmware_version",         "type": "uint8",                        "address": 6,       "writable": 0 },
        { "eeprom": 1,  "name": "id",                       "type": "uint8",                        "address": 7,       "writable": 1 },
        { "eeprom": 1,  "name": "baud_rate",                "type": "uint8",                        "address": 8,       "writable": 1 },
        { "eeprom": 1,  "name": "return_delay_time",        "type": "uint8",                        "address": 9,       "writable": 1 },
        { "eeprom": 1,  "name": "drive_mode",               "type": "uint8",                        "address": 10,      "writable": 1 },
        { "eeprom": 1,  "name": "operating_mode",           "type": "uint8",                        "address": 11,      "writable": 1 },
        { "eeprom": 1,  "name": "secondary_id",             "type": "uint8",                        "address": 12,      "writable": 1 },
        { "eeprom": 1,  "name": "protocol_version",         "type": "uint8",                        "address": 13,      "writable": 1 },
        { "eeprom": 1,  "name": "___RESERVED01",            "type": "uint8a-fixed", "width": 6,     "address": 14,      "writable": 1 },
        { "eeprom": 1,  "name": "homing_offset",            "type": "int32",                        "address": 20,      "writable": 1 },
        { "eeprom": 1,  "name": "moving_threshold",         "type": "uint32",                       "address": 24,      "writable": 1 },
        { "eeprom": 1,  "name": "___RESERVED02",            "type": "uint8a-fixed", "width": 3,     "address": 28,      "writable": 1 },
        { "eeprom": 1,  "name": "temperature_limit",        "type": "uint8",                        "address": 31,      "writable": 1 },
        { "eeprom": 1,  "name": "max_voltage_limit",        "type": "uint16",                       "address": 32,      "writable": 1 },
        { "eeprom": 1,  "name": "min_voltage_limit",        "type": "uint16",                       "address": 34,      "writable": 1 },
        { "eeprom": 1,  "name": "pwm_limit",                "type": "uint16",                       "address": 36,      "writable": 1 },
        { "eeprom": 1,  "name": "current_limit",            "type": "uint16",                       "address": 38,      "writable": 1 },
        { "eeprom": 1,  "name": "acceleration_limit",       "type": "uint32",                       "address": 40,      "writable": 1 },
        { "eeprom": 1,  "name": "velocity_limit",           "type": "uint32",                       "address": 44,      "writable": 1 },
        { "eeprom": 1,  "name": "max_position_limit",       "type": "int32",                        "address": 48,      "writable": 1 },
        { "eeprom": 1,  "name": "min_position_limit",       "type": "int32",                        "address": 52,      "writable": 1 },
        { "eeprom": 1,  "name": "___RESERVED03",            "type": "uint8a-fixed", "width": 7,     "address": 56,      "writable": 1 },
        { "eeprom": 1,  "name": "shutdown",                 "type": "uint8",                        "address": 63,      "writable": 1 },
        
        # RAM
        { "eeprom": 0,  "name": "torque_enable",            "type": "uint8",                        "address": 64,      "writable": 1 },
        { "eeprom": 0,  "name": "led",                      "type": "uint8",                        "address": 65,      "writable": 1 },
        { "eeprom": 0,  "name": "___RESERVED04",            "type": "uint8a-fixed", "width": 2,     "address": 66,      "writable": 1 },
        { "eeprom": 0,  "name": "status_return_level",      "type": "uint8",                        "address": 68,      "writable": 1 },
        { "eeprom": 0,  "name": "registered_instruction",   "type": "uint8",                        "address": 69,      "writable": 0 },
        { "eeprom": 0,  "name": "hardware_error_status",    "type": "uint8",                        "address": 70,      "writable": 0 },
        { "eeprom": 0,  "name": "___RESERVED05",            "type": "uint8a-fixed", "width": 5,     "address": 71,      "writable": 1 },
        { "eeprom": 0,  "name": "velocity_i_gain",          "type": "int16",                        "address": 76,      "writable": 1 },
        { "eeprom": 0,  "name": "velocity_p_gain",          "type": "int16",                        "address": 78,      "writable": 1 },
        { "eeprom": 0,  "name": "position_d_gain",          "type": "int16",                        "address": 80,      "writable": 1 },
        { "eeprom": 0,  "name": "position_i_gain",          "type": "int16",                        "address": 82,      "writable": 1 },
        { "eeprom": 0,  "name": "position_p_gain",          "type": "int16",                        "address": 84,      "writable": 1 },
        { "eeprom": 0,  "name": "___RESERVED06",            "type": "uint8a-fixed", "width": 2,     "address": 86,      "writable": 1 },
        { "eeprom": 0,  "name": "feedforward_2nd_gain",     "type": "int16",                        "address": 88,      "writable": 1 },
        { "eeprom": 0,  "name": "feedforward_1st_gain",     "type": "int16",                        "address": 90,      "writable": 1 },
        { "eeprom": 0,  "name": "___RESERVED07",            "type": "uint8a-fixed", "width": 6,     "address": 92,      "writable": 1 },
        { "eeprom": 0,  "name": "bus_watchdog",             "type": "uint8",                        "address": 98,      "writable": 1 },
        { "eeprom": 0,  "name": "___RESERVED08",            "type": "uint8a-fixed", "width": 1,     "address": 99,      "writable": 1 },
        { "eeprom": 0,  "name": "goal_pwm",                 "type": "uint16",                       "address": 100,     "writable": 1 },
        { "eeprom": 0,  "name": "goal_current",             "type": "uint16",                       "address": 102,     "writable": 1 },
        { "eeprom": 0,  "name": "goal_velocity",            "type": "int32",                        "address": 104,     "writable": 1 },
        { "eeprom": 0,  "name": "profile_acceleration",     "type": "int32",                        "address": 108,     "writable": 1 },
        { "eeprom": 0,  "name": "profile_velocity",         "type": "int32",                        "address": 112,     "writable": 1 },
        { "eeprom": 0,  "name": "goal_position",            "type": "int32",                        "address": 116,     "writable": 1 },
        { "eeprom": 0,  "name": "realtime_tick",            "type": "uint16",                       "address": 120,     "writable": 0 },
        { "eeprom": 0,  "name": "moving",                   "type": "uint8",                        "address": 122,     "writable": 0 },
        { "eeprom": 0,  "name": "moving_status",            "type": "uint8",                        "address": 123,     "writable": 0 },
        { "eeprom": 0,  "name": "present_pwm",              "type": "uint16",                       "address": 124,     "writable": 0 },
        { "eeprom": 0,  "name": "present_current",          "type": "uint16",                       "address": 126,     "writable": 0 },
        { "eeprom": 0,  "name": "present_velocity",         "type": "int32",                        "address": 128,     "writable": 0 },
        { "eeprom": 0,  "name": "present_position",         "type": "int32",                        "address": 132,     "writable": 0 },
        { "eeprom": 0,  "name": "velocity_trajectory" ,     "type": "int32",                        "address": 136,     "writable": 0 },
        { "eeprom": 0,  "name": "position_trajectory",      "type": "int32",                        "address": 140,     "writable": 0 },
        { "eeprom": 0,  "name": "present_input_voltage",    "type": "uint16",                       "address": 144,     "writable": 0 },
        { "eeprom": 0,  "name": "present_temperature",      "type": "int8",                         "address": 146,     "writable": 0 },
    ]
                
class ControlTablePro(ControlTable):
    
    pass
    
