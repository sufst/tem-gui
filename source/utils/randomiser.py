"""Module for generating random data for testing purposes.

  This module generates random data for testing purposes. It is used to simulate BMS CAN messages.
  To enable the generation of random data, set the RANDOM_DATA_DEFINITION flag in main.py to True.
"""

from typing import List
import random
import struct

from components.Module import Module
from utils.constants import N_THERMISTORS_PER_MODULE, BYTE_ORDER, IDs


def generate_random_can_data(module_id: int, modules: List[Module]) -> bytes:
  """ Generate random BMS data

  Used to simulate BMS CAN messages.

  Args:
      module_id (int): ID of the module in range [0, N_MODULES]
      modules (List[Module]): List of modules in the system

  Returns:
      bytes: Randomly generated CAN message payload
  """

  # Randomly choose between BMS_BC_ID and GENERAL_BC_ID
  can_id = random.choice([IDs.BMS_BC_ID, IDs.GENERAL_BC_ID])

  if can_id == IDs.BMS_BC_ID:
    min_temp = 80
    max_temp = -20
    lowest_therm_id, highest_therm_id = 0,0
    sum_temp = 0
    for i in range(len(modules[module_id].thermistors)):
      thermistor = modules[module_id].thermistors[i]
      print(f'Thermistor {i} temp: {thermistor.temp}')
      sum_temp += thermistor.temp
      if thermistor.temp < min_temp:
        min_temp = thermistor.temp
        lowest_therm_id = i
      if thermistor.temp > max_temp:
        max_temp = thermistor.temp
        highest_therm_id = i
    avg_temp =  int(sum_temp / len(modules[module_id].thermistors))
    num_thermistors = modules[module_id].number_of_thermistors

    checksum = (module_id + min_temp + max_temp + avg_temp + num_thermistors +
                highest_therm_id + lowest_therm_id) % 256
    print(f'Module ID: {module_id} Number of thermistors: {num_thermistors}|min_temp: {min_temp}|max_temp: {max_temp}|highest_id {highest_therm_id}|lowest id: {lowest_therm_id}')
    # Match module message byte pattern
    payload = struct.pack('>BbbbBBBB', module_id, min_temp, max_temp, avg_temp,
                            num_thermistors, highest_therm_id, lowest_therm_id, checksum)
  else:  # GENERAL_BC_ID
      num_thermistors = random.randint(1, N_THERMISTORS_PER_MODULE)
      therm_id = (module_id+1) * 80 + random.randint(0, num_thermistors - 1)
      temp = random.randint(-20, 80)
      min_temp = random.randint(-20, temp)
      max_temp = random.randint(temp, 80)
      highest_therm_id = random.randint(0, N_THERMISTORS_PER_MODULE - 1)
      lowest_therm_id = random.randint(0, highest_therm_id)
      print(f'ID: {therm_id}|Temperature: {temp}|Number of thermistors: {num_thermistors}|min_temp: {min_temp}|max_temp: {max_temp}|highest_id {highest_therm_id}|lowest id: {lowest_therm_id}')
      # Match general message byte pattern
      payload = struct.pack('>HbBbbBB', therm_id, temp, num_thermistors, min_temp,
                            max_temp, highest_therm_id, lowest_therm_id)

  return can_id.to_bytes(4, byteorder=BYTE_ORDER) + payload