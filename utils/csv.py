import csv

def create_csv_file(filepath, header, data):
  with open(filepath, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()
    writer.writerows(data)
