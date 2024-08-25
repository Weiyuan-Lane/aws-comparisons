import boto3
import os
from utils.aws_regions import get_region_code_to_name_map
from utils.aws_pricing_plans import get_pricing_for
from utils.csv import create_csv_file
from dotenv import load_dotenv
load_dotenv()

def get_csv_from(region_to_saving_plan_map):
  base_region_code = os.getenv("BASE_REGION")
  region_codes = os.getenv("COMPARISON_REGIONS").split(",")
  region_codes.insert(0, base_region_code)
  header_row = ["Plan"]
  code_to_name_map = get_region_code_to_name_map()

  saving_plan_set = set()
  for saving_plan_map in region_to_saving_plan_map.values():
    saving_plan_set = saving_plan_set.union(set(saving_plan_map.keys()))
  saving_plan_keys = sorted([str(item) for item in saving_plan_set])

  # Get header row first
  for region_code in region_codes:
    header_row.append(f"{code_to_name_map[region_code]} - {region_code}")

  # Get all rows
  all_rows = []
  for saving_plan_key in saving_plan_keys:
    row = { "Plan": saving_plan_key }
    for i, column_id in enumerate(header_row[1:]):
      region_code = region_codes[i]
      saving_plan_map = region_to_saving_plan_map[region_code]

      if saving_plan_key in saving_plan_map:
        row[column_id] = saving_plan_map[saving_plan_key]
      else:
        row[column_id] = '-'

    all_rows.append(row)

  return header_row, all_rows

if __name__ == "__main__":
  region_to_saving_plan_map = get_pricing_for(["t4g.xlarge", "c7g.xlarge", "r6i.xlarge"])
  header_row, all_rows = get_csv_from(region_to_saving_plan_map)
  create_csv_file("dist/saving_plans_by_region_comparison.csv", header_row, all_rows)
