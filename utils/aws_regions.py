from functools import cache
import os
import yaml
from dotenv import load_dotenv
load_dotenv()

@cache
def get_region_list():
  with open('assets/regions.yaml', 'r') as file:
    regions_data = yaml.safe_load(file)
  return regions_data

def get_all_region_names():
  regions_data = get_region_list()
  region_names = [region['name'] for region in regions_data]
  return region_names

def get_all_region_codes():
  regions_data = get_region_list()
  region_codes = [region['code'] for region in regions_data]
  return region_codes

def get_region_code_to_name_map():
  regions_data = get_region_list()
  region_map = {}
  for region in regions_data:
    region_map[region['code']] = region['name']
  return region_map

def get_ordered_regions():
  base_region = os.getenv("BASE_REGION")
  region_codes = get_all_region_codes()
  region_codes = sorted(region_codes)

  if base_region in region_codes:
    region_codes.remove(base_region)
    region_codes.insert(0, base_region)

  return region_codes