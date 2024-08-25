import boto3
import os
from utils.aws_regions import get_all_region_names, get_all_region_codes, get_region_code_to_name_map, get_ordered_regions
from utils.csv import create_csv_file
from dotenv import load_dotenv
load_dotenv()

def list_available_services():
  session = boto3.Session()
  available_services = session.get_available_services()
  return available_services

def list_available_region_codes_by(service):
  session = boto3.Session()
  regions = session.get_available_regions(service)
  return regions

def get_csv_header_row():
  region_codes = get_ordered_regions()
  code_to_name_map = get_region_code_to_name_map()
  header_row = ["Service"]
  for region_code in region_codes:
    header_row.append(f"{code_to_name_map[region_code]} - {region_code}")
  return header_row

def get_csv_from(all_regions_to_service_map):
  service_uniq_set = set()
  for region_to_service_set in all_regions_to_service_map.values():
    service_uniq_set = service_uniq_set.union(region_to_service_set)
  services = sorted([str(item) for item in service_uniq_set])

  region_codes = get_ordered_regions()
  header_row = get_csv_header_row()
  all_rows = []

  # Add overall column
  row = { header_row[0]: "(Overall %)" }
  for i, column_id in enumerate(header_row[1:]):
    region_code = region_codes[i]
    if region_code not in all_regions_to_service_map:
      row[column_id] = 0
      continue

    region_to_service_set = all_regions_to_service_map[region_code]
    row[column_id] = round(len(region_to_service_set) / len(services), 3)
    services
  all_rows.append(row)


  # build main columns
  for service in services:
    row = { header_row[0]: service }

    for i, column_id in enumerate(header_row[1:]):
      region_code = region_codes[i]
      if region_code not in all_regions_to_service_map:
        row[column_id] = False
        continue

      region_to_service_set = all_regions_to_service_map[region_code]
      row[column_id] = service in region_to_service_set

    all_rows.append(row)

  return header_row, all_rows

if __name__ == "__main__":
  services = list_available_services()
  all_regions_to_service_map = {}

  for service in services:
    region_codes = list_available_region_codes_by(service)

    for region_code in region_codes:
      if region_code not in all_regions_to_service_map:
        all_regions_to_service_map[region_code] = set(service)
      else :
        all_regions_to_service_map[region_code].add(service)

  header_row, all_rows = get_csv_from(all_regions_to_service_map)
  create_csv_file("dist/all_service_by_region_comparison.csv", header_row, all_rows)
