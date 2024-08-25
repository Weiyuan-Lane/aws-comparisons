import boto3
import os
from utils.aws_regions import get_region_code_to_name_map
from utils.aws_instances import get_ec2_instances_by, get_ondemand_pricing_for, get_3_yr_standard_reserved_pricing_for
from utils.csv import create_csv_file
from dotenv import load_dotenv
load_dotenv()

def get_csv_from(ec2_instance_to_region_pricing_map):
  base_region_code = os.getenv("BASE_REGION")
  region_codes = os.getenv("COMPARISON_REGIONS").split(",")
  region_codes.insert(0, base_region_code)
  header_row = ["InstanceType"]
  code_to_name_map = get_region_code_to_name_map()

  # Get header row first
  for region_code in region_codes:
    header_row.append(f"{code_to_name_map[region_code]} - {region_code}")

  # Get all rows
  all_rows = []
  ec2_instance_keys = sorted(ec2_instance_to_region_pricing_map.keys())
  for ec2_instance_key in ec2_instance_keys:
    row = { "InstanceType": ec2_instance_key }
    region_pricing_map = ec2_instance_to_region_pricing_map[ec2_instance_key]

    for i, column_id in enumerate(header_row[1:]):
      region_code = region_codes[i]

      if region_code in region_pricing_map and region_pricing_map[region_code]['currency'] == 'USD':
        row[column_id] = region_pricing_map[region_code]["pricing_value"]
      else:
        row[column_id] = "-"

    all_rows.append(row)

  return header_row, all_rows

def save_pricing_date_csv_to(filepath, operating_system, purchase_term):
  base_region_code = os.getenv("BASE_REGION")
  region_codes = os.getenv("COMPARISON_REGIONS").split(",")
  region_codes.append(base_region_code)

  ec2_instances_in_region = get_ec2_instances_by(base_region_code)
  ec2_instance_types = [ec2_instance["InstanceType"] for ec2_instance in ec2_instances_in_region]

  ec2_instance_to_region_pricing_map = {}
  for ec2_instance_type in ec2_instance_types:
    if purchase_term == 'OnDemand':
      ec2_instance_to_region_pricing_map[ec2_instance_type] = get_ondemand_pricing_for(ec2_instance_type, operating_system)
    elif purchase_term == 'Reserved':
      ec2_instance_to_region_pricing_map[ec2_instance_type] = get_3_yr_standard_reserved_pricing_for(ec2_instance_type, operating_system)

  header_row, all_rows = get_csv_from(ec2_instance_to_region_pricing_map)
  create_csv_file(filepath, header_row, all_rows)

if __name__ == "__main__":
  save_pricing_date_csv_to("dist/ec2_pricing_linux_on_demand_by_region_comparison.csv", "Linux", "OnDemand")
  save_pricing_date_csv_to("dist/ec2_pricing_linux_reserved_by_region_comparison.csv", "Linux", "Reserved")

  save_pricing_date_csv_to("dist/ec2_pricing_windows_on_demand_by_region_comparison.csv", "Windows", "OnDemand")
  save_pricing_date_csv_to("dist/ec2_pricing_windows_reserved_by_region_comparison.csv", "Windows", "Reserved")


