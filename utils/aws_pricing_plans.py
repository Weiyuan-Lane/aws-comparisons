import boto3
import json
from dotenv import load_dotenv
load_dotenv()

def get_pricing_for(instance_types):
  client = boto3.client('savingsplans', region_name = 'us-east-1')

  filters = [
    {'name': 'instanceType', 'values': instance_types},
    {'name': 'productDescription', 'values': ['Linux/UNIX']},
  ]

  response = client.describe_savings_plans_offering_rates(
    serviceCodes=['AmazonEC2'],
    filters=filters
  )

  pricing_by_region = {}

  # Process and print the rates
  for search_result in response['searchResults']:
    if 'savingsPlanOffering' not in search_result and 'planDescription' not in search_result['savingsPlanOffering']:
      continue
    if 'savingsPlanOffering' not in search_result and 'currency' not in search_result['savingsPlanOffering'] and search_result['savingsPlanOffering']['currency'] != 'USD':
      continue
    if 'unit' not in search_result and search_result['unit'] != 'Hrs':
      continue
    if 'rate' not in search_result and float(search_result['rate']) > 0:
      continue
    if 'properties' not in search_result:
      continue

    search_result_property_map = {}
    for property in search_result['properties']:
      search_result_property_map[property['name']] = property['value']
    if 'region' not in search_result_property_map:
      continue
    if 'instanceFamily' not in search_result_property_map:
      continue
    if 'instanceType' not in search_result_property_map:
      continue
    if 'productDescription' not in search_result_property_map or search_result_property_map["productDescription"] != "Linux/UNIX":
      continue
    if 'tenancy' not in search_result_property_map or search_result_property_map["tenancy"] != "shared":
      continue

    region = search_result_property_map['region']
    region_free_identifier= search_result['savingsPlanOffering']['planDescription'].replace(f" in {region}", "")
    identifier = f"{region_free_identifier} - Family: {search_result_property_map['instanceFamily']} - Instance: {search_result_property_map['instanceType']}"

    if region not in pricing_by_region:
      pricing_by_region[region] = {
        identifier: float(search_result['rate'])
      }
    else:
      pricing_by_region[region][identifier] = float(search_result['rate'])

  return pricing_by_region



