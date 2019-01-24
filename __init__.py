"""
This module provides protocol and packet definitions for communicating with
newer Robotis Dynamixel servos that implement version 2 of the Dynamixel
protocol. In addition to the basic protocol, it also abstracts common sets of
transactions (such as writing new values to control table registers) into simple
servo class methods, so the application does not require knowledge or use of the
underlying protocol directly.
"""

# .py files
from .protocol import *
from .control_table import *
from .servo import *
from .device import *
