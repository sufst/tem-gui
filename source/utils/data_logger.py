from typing import List
from time import sleep, time
from datetime import datetime
from utils.file_writer import write_csv_file
from utils.constants import MODULE_CSV_FORMAT, THERMISTOR_CSV_FORMAT, MODULE_CSV_ENDING, THERMISTOR_CSV_ENDING, LOGGING_INTERVAL, LOGGING_START

class DataLogger:
  moduleData: List[str] = [MODULE_CSV_FORMAT]
  thermistorData: List[str] = [THERMISTOR_CSV_FORMAT]
  path_identifier: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  def __init__(self, type):
    self.type = type

  def logging_thread(self, modules, get_app_quit):
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
    if self.type == "csv":
      print("Writing to CSV files")
      write_csv_file(self.moduleData, self.path_identifier + MODULE_CSV_ENDING)
      write_csv_file(self.thermistorData,self.path_identifier + THERMISTOR_CSV_ENDING)
    else:
      print("Unknown type")
