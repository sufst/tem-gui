"""This module contains the functions to decode the CAN messages.

  The module contains the functions to decode the CAN messages and update the module and thermistor values.
"""

from typing import List
import math

from components.Module import Module
from utils.constants import BYTE_ORDER, IDs


def decode_can_data(can_id: bytes, data: bytes, modules: List[Module]) -> None:
  """Decode the CAN data

  Args:
      can_id (bytes): CAN ID of the message. 0x1839F38X, where X is the module ID
      data (bytes): The payload of the message
      modules (List[Module]): List of modules in the system
  """
  if (can_id >> 4) == (IDs.GENERAL_BC_ID >> 4):
    _decode_gbc(data, modules)
  elif (can_id >> 4) == (IDs.BMS_BC_ID >> 4):
    _decode_bmsbc(data, modules)
  else:
    print(f"Unknown CAN ID: {can_id}")

def _decode_bmsbc(payload: bytes, modules: List[Module]) -> None:
  """Decode the BMS Broadcast message

  Args:
    payload (bytes): The payload of the message
    modules (List[Module]): List of modules in the system
  """
  # Extract values from payload
  module_id = int.from_bytes(payload[0:1], byteorder=BYTE_ORDER, signed=False)
  modules[module_id].min_temp = int.from_bytes(payload[1:2], byteorder=BYTE_ORDER, signed=True)
  modules[module_id].max_temp = int.from_bytes(payload[2:3], byteorder=BYTE_ORDER, signed=True)
  modules[module_id].avg_temp = int.from_bytes(payload[3:4], byteorder=BYTE_ORDER, signed=True)
  # Check value with checksum
  #checksum = int.from_bytes(payload[7:8], byteorder=BYTE_ORDER, signed=False)
  #if checksum != (module_id + modules[module_id].min_temp + modules[module_id].max_temp + modules[module_id].avg_temp + 0x41) % 256: # 0x41 is a magic number
  #  print(f"Checksum failed for module {module_id}")
  # print(f"Module {module_id+1}\n\tMin: {modules[module_id].min_temp} °C\n\tAvg: {modules[module_id].avg_temp} °C\n\tMax: {modules[module_id].max_temp} °C")

def _decode_gbc(payload: bytes, modules: List[Module]) -> None:
  """Decode the General Broadcast message

  Args:
      payload (bytes): The payload of the message
      modules (List[Module]): List of modules in the system
  """
  rel_id = int.from_bytes(payload[0:2], byteorder=BYTE_ORDER, signed=False) # Relative ID
  module_id = math.floor(rel_id / 80)
  therm_id = rel_id % 80
  new_temp = int.from_bytes(payload[2:3], byteorder=BYTE_ORDER, signed=True)
  number_of_thermistors = int.from_bytes(payload[3:4], byteorder=BYTE_ORDER, signed=False)

  with modules[module_id-1].lock:
    # print(f'Thermistors length: {len(modules[module_id-1].thermistors)}')
    # print(f'Modules length: {len(modules)}')
    modules[module_id-1].number_of_thermistors = number_of_thermistors
    modules[module_id-1].thermistors[therm_id].update_temp(new_temp)