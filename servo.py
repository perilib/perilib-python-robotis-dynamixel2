import perilib

from .control_table import *

class Servo():
    
    models = {
        12:     { "name": "AX-12A" },
        300:    { "name": "AX-12W" },
        18:     { "name": "AX-18A" },

        10:     { "name": "RX-10" },
        24:     { "name": "RX-24F" },
        28:     { "name": "RX-28" },
        64:     { "name": "RX-64" },

        107:    { "name": "EX-106" },

        104:    { "name": "MX-12W" },
        29:     { "name": "MX-28" },
        30:     { "name": "MX-28-2" },
        310:    { "name": "MX-64" },
        311:    { "name": "MX-64-2" },
        320:    { "name": "MX-106" },
        321:    { "name": "MX-106-2" },

        350:    { "name": "XL-320" },
        1060:   { "name": "XL430-W250", "control_table_class": ControlTableX },

        1030:   { "name": "XM430-W250", "control_table_class": ControlTableX },
        1020:   { "name": "XM430-W250", "control_table_class": ControlTableX },
        1130:   { "name": "XM540-W150", "control_table_class": ControlTableX },
        1120:   { "name": "XM540-W270", "control_table_class": ControlTableX },

        1050:   { "name": "XH430-V210", "control_table_class": ControlTableX },
        1040:   { "name": "XH430-V235", "control_table_class": ControlTableX },
        1010:   { "name": "XH430-W210", "control_table_class": ControlTableX },
        1000:   { "name": "XH430-W350", "control_table_class": ControlTableX },

        35072:  { "name": "PRO-L42-10-S300-R" },
        37928:  { "name": "PRO-L54-30-S400-R" },
        37896:  { "name": "PRO-L54-30-S500-R" },
        38176:  { "name": "PRO-L54-50-S290-R" },
        38152:  { "name": "PRO-L54-50-S500-R" },

        43288:  { "name": "PRO-M42-10-S260-R" },
        46096:  { "name": "PRO-M54-40-S250-R" },
        46352:  { "name": "PRO-M54-60-S250-R" },

        51200:  { "name": "PRO-H42-20-S300-R" },
        53768:  { "name": "PRO-H54-100-S500-R" },
        54024:  { "name": "PRO-H54-200-S500-R" },

        2000:   { "name": "PRO-H42P-020-S300-R" },
        2010:   { "name": "PRO-H54P-100-S500-R" },
        2020:   { "name": "PRO-H54P-200-S500-R" },
    }
    
    def __init__(self, id=None, model_number=None, firmware_version=None, device=None):
        self.id = id
        self.model_number = model_number
        self.firmware_version = firmware_version
        self.device = device
        self.control_table = Servo.models[self.model_number]["control_table_class"]()
        
    def __str__(self):
        id_str = ("#%d" % self.id) if self.id is not None else "unidentified servo"
        model_number_str = Servo.models[self.model_number]["name"] if self.model_number is not None else "unknown model"
        firmware_version_str = self.firmware_version if self.firmware_version is not None else "-unknown"
        device_str = str(self.device) if self.device is not None else "unidentified device"
        return "%s (%s @ v%s) on %s" % (id_str, model_number_str, firmware_version_str, device_str)

    def ping(self):
        return self.device.stream.parser_generator.send_and_wait("inst_ping", id=self.id)

    def read_control_table(self):
        packet = self.device.stream.parser_generator.send_and_wait("inst_read", id=self.id, address=0, length=self.control_table.size)
        if packet is not None and packet is not False:
            self.control_table.populate_data_from_buffer(packet.payload["data"])
        return packet
        
    def update_value(self, field_name, value):
        field = self.control_table.get_field_info(field_name)
        data = perilib.protocol.Protocol.pack_values({field_name: value}, [field])
        packet = self.device.stream.parser_generator.send_and_wait("inst_write", id=self.id, address=field["address"], data=data)
        return packet
        
