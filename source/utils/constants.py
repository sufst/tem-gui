"""Constants for the TEM GUI."""

from dataclasses import dataclass
from colour import Color

TITLE = "TEM GUI"                       # Title of the GUI
ICON = r"./resources/images/stag.svg"   # Icon for the GUI

N_MODULES = 9                                         # Number of modules in the system
N_THERMISTORS_PER_MODULE = 24                         # Number of thermistors per module
N_THERMISTORS = N_MODULES * N_THERMISTORS_PER_MODULE  # Total number of thermistors in the system

SERIAL_PORT_LINUX = "/dev/ttyACM0"    # Serial port for Linux
SERIAL_PORT_WINDOW = "COM0"           # Serial port for Windows
SERIAL_PORT_MAC = ""                  # Serial port for MacOS

SERIAL_BAUD_RATE = 115200   # Baud rate for serial communication
BYTE_ORDER= "big"           # Byte order for serial communication

COLOR_GRADIENT = list(Color("green").range_to(Color("red"),100))  # Colour gradient for temperature display
MIN_TEMP = -20              # Minimum temperature for the system
MAX_TEMP = 80               # Maximum temperature for the system

MODULE_CSV_FORMAT = ["Module ID", "Min Temp", "Max Temp", "Avg Temp", "Number of Thermistors", "Timestamp"]   # CSV format for module data
THERMISTOR_CSV_FORMAT = ["Module ID", "Thermistor ID", "Temperature", "Timestamp"]                            # CSV format for thermistor data

MODULE_CSV_ENDING = "_modules.csv"            # Ending for module CSV files
THERMISTOR_CSV_ENDING = "_thermistors.csv"    # Ending for thermistor CSV files
LOG_FOLDER = "logs"                           # Folder for log files

LOGGING_START = 1           # Start logging at this time in seconds from the start
LOGGING_INTERVAL = 5        # Logging interval in seconds

@dataclass
class IDs:
  BMS_BC_ID: int = int("1839F380", 16)     # BMS Broadcast CAN ID
  GENERAL_BC_ID: int = int("1838F380", 16) # General Broadcast CAN ID