"""Thermistor class definition"""

from kivy.app import EventDispatcher
from kivy.properties import NumericProperty

import math
from colour import Color

from utils.constants import COLOR_GRADIENT, MIN_TEMP, MAX_TEMP


# Hard-code currently dead thermistors
dead_therms = [
  [],
  [3],
  [],
  [],
  [],
  [],
  [],
  [],
  []
]


class Thermistor(EventDispatcher):
  """A class used to represent a Thermistor

  Attributes:
      module_id: An integer representing the module ID in which the thermistor is located [0 to N_MODULES - 1].
      therm_id: An integer representing the thermistor ID in the module [0 to N_THERMISTORS_PER_MODULE - 1].
      temp: A NumericProperty representing the current temperature of the thermistor. Default is 0.
      max_temp: An integer representing the maximum temperature of the thermistor. Default is 0.
      min_temp: An integer representing the minimum temperature of the thermistor. Default is 0.
      temp_label: A StringProperty representing the label of the temperature. Default is None. Used for Kivy GUI.
  """
  temp = NumericProperty(0)
  def __init__(self, module_id: int, therm_id: int):
    """Initialises the Thermistor instance

    Args:
        module_id (int): An integer representing the module ID in which the thermistor is located [0 to N_MODULES - 1].
        therm_id (int): An integer representing the thermistor ID in the module [0 to N_THERMISTORS_PER_MODULE - 1].
    """
    self.module_id = module_id
    self.therm_id = therm_id
    self.max_temp = 0
    self.min_temp = 0
    self.temp_label = None

  def __repr__(self) -> str:
    return f"{self.module_id}:{self.therm_id} = {self.temp} °C\t(min: {self.min_temp}, max: {self.max_temp})"

  def update_temp(self, new_temp: int):
    """Updates the temperature of the thermistor

    Args:
        new_temp (int): The new temperature value to update the thermistor with.
    """
    self.temp = new_temp
    self.min_temp = min(self.min_temp, new_temp)
    self.max_temp = max(self.max_temp, new_temp)

    print(f"Temperature for thermistor {self.module_id}:{self.therm_id} was updated to {self.temp} °C")

  def get_temp_colour(self, value: int, min_val: int, max_val: int):
    """Returns the colour of the temperature based on the value

    Args:
        value (int): The temperature value to get the colour for.
        min_val (int): The minimum temperature value(The "greenest" colour value).
        max_val (int): The maximum temperature value(The "reddest" colour value).

    Returns:
        tuple: A tuple representing the RGB colour value of the temperature.
    """
    if max_val - min_val != 0:
      proportion = (value - min_val) / (max_val - min_val)
      # print(f'Proportion: {proportion}, min: {min_val}, max: {max_val}, current: {value}')
      index = math.floor(proportion * (len(COLOR_GRADIENT) - 1))
      # print(f'Colour index: {index}, min: {self.min_temp}, max: {self.max_temp}, current: {self.temp}')
      index = max((0, index))
      index = min(index, 99)
      colour = COLOR_GRADIENT[index].get_rgb() + (1,)
      return colour

  def temp_callback(self, instance, value):
    """Callback function for the temperature change event"""
    self.max_temp = max(self.temp, self.max_temp)
    self.min_temp = min(self.temp, self.min_temp)

    if self.therm_id in dead_therms[self.module_id]:
      self.temp_label.text = "N/A"
      self.temp_label.color = Color("blue").get_rgb()
    else:
      self.temp_label.text = str(self.temp) + "°C "
      self.temp_label.color = self.get_temp_colour(self.temp, MIN_TEMP, MAX_TEMP)