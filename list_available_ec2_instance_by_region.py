import os
from utils.aws_regions import get_all_region_codes, get_ordered_regions, get_region_code_to_name_map
from utils.aws_instances import get_ec2_instances_by, properties_to_retrieve
from utils.csv import create_csv_file
from dotenv import load_dotenv
load_dotenv()

def get_csv_from(ec2_instance_map, all_regions_to_ec2_instance_map):
  region_codes = get_ordered_regions()
  ec2_instance_keys = sorted(ec2_instance_map.keys())
  ec2_property_keys = [".".join(property_list) for property_list in properties_to_retrieve]
  all_rows = []

  header_row = ec2_property_keys.copy()
  code_to_name_map = get_region_code_to_name_map()
  realigned_region_codes = []
  for region_code in region_codes:
    if region_code in all_regions_to_ec2_instance_map:
      header_row.append(f"{code_to_name_map[region_code]} - {region_code}")
      realigned_region_codes.append(region_code)

  for ec2_instance_key in ec2_instance_keys:
    row = {}
    for ec2_property_key in ec2_property_keys:
      row[ec2_property_key] = ec2_instance_map[ec2_instance_key][ec2_property_key]

    for i, column_id in enumerate(header_row[len(ec2_property_keys):]):
      region_code = realigned_region_codes[i]
      row[column_id] = ec2_instance_key in all_regions_to_ec2_instance_map[region_code]

    all_rows.append(row)

  return header_row, all_rows

if __name__ == "__main__":
  ec2_instance_map = {}
  all_regions_to_ec2_instance_map = {}

  region_codes = os.getenv("COMPARISON_REGIONS").split(",")
  region_codes.append(os.getenv("BASE_REGION"))

  for region_code in region_codes:
    try:
      ec2_instances_in_region = get_ec2_instances_by(region_code)
    except Exception as e:
      print(f"Not able to retrieve for region {region_code}, continuing")
      continue

    # Build unique set of all ec2 instance types
    for ec2_instance in ec2_instances_in_region:
      if ec2_instance["InstanceType"] not in ec2_instance_map:
        ec2_instance_map[ec2_instance["InstanceType"]] = ec2_instance

    all_regions_to_ec2_instance_map[region_code] = [ec2_instance["InstanceType"] for ec2_instance in ec2_instances_in_region]

  header_row, all_rows = get_csv_from(ec2_instance_map, all_regions_to_ec2_instance_map)
  create_csv_file("dist/ec2_by_region_comparison.csv", header_row, all_rows)
