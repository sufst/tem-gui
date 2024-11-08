import csv
import os

from utils.constants import LOG_FOLDER

dir = os.path.dirname(__file__)
log_folder = folder = os.path.join(dir,"../../" ,LOG_FOLDER)

def check_log_dir_exists():
  if not os.path.exists(log_folder):
    os.makedirs(log_folder)

def write_csv_file(content, file_path):
  check_log_dir_exists()
  file_path = os.path.join(log_folder, file_path)
  with open(file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(content)