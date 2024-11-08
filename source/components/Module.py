"""Module class definition"""

from kivy.app import EventDispatcher
from kivy.properties import NumericProperty

from threading import Lock
from typing import List

from components.Thermistor import Thermistor
from utils.constants import N_THERMISTORS_PER_MODULE

class Module(EventDispatcher):
  """A class used to represent a Module

  Attributes:
      n_module (int): An integer representing the module ID [0 to N_MODULES - 1].
      max_temp (int): An integer representing the maximum temperature of the module. Default is 0.
      avg_temp (int): An integer representing the average temperature of the module. Default is 0.
      min_temp (int): An integer representing the minimum temperature of the module. Default is 0.
      number_of_thermistors (int): An integer representing the number of thermistors in the module. Default is N_THERMISTORS_PER_MODULE.
  """
  max_temp = NumericProperty(0)
  avg_temp = NumericProperty(0)
  min_temp = NumericProperty(0)
  number_of_thermistors = NumericProperty(N_THERMISTORS_PER_MODULE)

  def __init__(self, module_id: int, therms: List[Thermistor]):
    """Initialises the Module instance

    Args:
        module_id (int): An integer representing the module ID [0 to N_MODULES - 1].
        therms (List[Thermistor]): A list of Thermistor instances in the module.
    """
    self.module_id = module_id
    self.lock = Lock()
    self.thermistors: List[Thermistor] = therms
    self.label = None

  def temp_callback(self, instance, value):
    """Callback function for the temperature change event"""
    self.label.text = f"[b]Module {self.module_id}[/b]\nMin: {self.min_temp}\nAvg: {self.avg_temp}\nMax:{self.max_temp}\nN° of thermistors: {self.number_of_thermistors}"
