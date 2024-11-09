"""This module contains functions for writing to files

  Example:
    To write to a file, use the write_csv_file function:
      write_csv_file([["Column1", "Columns2"],["Value1", "Value2"],...,["Value_n-1", "Value_n"]], "example.csv")
"""

import csv
import os
from typing import List

from utils.constants import LOG_FOLDER

# Get the log folder
dir = os.path.dirname(__file__)
log_folder = folder = os.path.join(dir,"../../" ,LOG_FOLDER)

def check_log_dir_exists():
  """Check if the log folder exists, if not create it"""
  if not os.path.exists(log_folder):
    os.makedirs(log_folder)

def write_csv_file(content:List[List[str]], file_path: str):
  """Write content to a csv file

  Args:
      content (List[List[str]]): The content to write to the file
      file_path (str): Name of the file to write to
  """
  check_log_dir_exists()
  file_path = os.path.join(log_folder, file_path)
  with open(file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(content)