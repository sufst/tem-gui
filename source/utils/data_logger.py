"""DataLogger module."""

from typing import List
from time import sleep, time
from datetime import datetime

from utils.file_writer import write_csv_file
from utils.constants import MODULE_CSV_FORMAT, THERMISTOR_CSV_FORMAT, MODULE_CSV_ENDING, THERMISTOR_CSV_ENDING, LOGGING_INTERVAL, LOGGING_START

class DataLogger:
  """A class used to represent a DataLogger.

  DataLogger is used to log the data from the modules and thermistors to a file.
  Note that the data is logged every LOGGING_INTERVAL seconds.

  Attributes:
    type (str): A string representing the type of the file to write to. Default is "csv".
    moduleData (List[List[str]]): A list of lists containing the module data. Default is [MODULE_CSV_FORMAT].
    thermistorData (List[str]): A list of lists containing the thermistor data. Default is [THERMISTOR_CSV_FORMAT].
    path_identifier (str): A string representing the path identifier. Default is the current date and time.
  """
  type: str = "csv"
  moduleData: List[List[str]] = [MODULE_CSV_FORMAT]
  thermistorData: List[str] = [THERMISTOR_CSV_FORMAT]
  path_identifier: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  def __init__(self, type="csv"):
    """Initialises the DataLogger instance.

    Args:
        type (str): A string representing the type of the file to write to. Default is "csv".
    """
    self.type = type

  def logging_thread(self, modules, get_app_quit):
    """The logging thread function.

    Args:
        modules (_type_): Modules to log data from.
        get_app_quit (_type_): Function to get the app quit status. Go to the main.py file to see the implementation.
    """
    start = time()
    while(not get_app_quit()):
      sleep(0.5)
      cur_time = time()
      time_diff = int(cur_time - start)
      if (time_diff != 0 and time_diff % LOGGING_INTERVAL == 0) or time_diff == LOGGING_START:
        for module in modules:
          self.moduleData.append([module.module_id, module.min_temp, module.max_temp, module.avg_temp, module.number_of_thermistors, time_diff])
          for thermistor in module.thermistors:
            self.thermistorData.append([thermistor.module_id, thermistor.therm_id, thermistor.temp, time_diff])
    self.stop_logging()

  def stop_logging(self):
    """Stop the logging process.

    This function is called when the logging process is stopped.
    Stop the logging process and write the data to the file.
    """
    if self.type == "csv":
      print("Writing to CSV files")
      write_csv_file(self.moduleData, self.path_identifier + MODULE_CSV_ENDING)
      write_csv_file(self.thermistorData,self.path_identifier + THERMISTOR_CSV_ENDING)
    else:
      print("Unknown type")
