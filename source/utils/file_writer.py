import csv

def write_csv_file(content, file_path):
  with open(file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(content)