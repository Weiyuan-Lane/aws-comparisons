import boto3
import json
from dotenv import load_dotenv
load_dotenv()

properties_to_retrieve = [
  ["InstanceType"],
  ["FreeTierEligible"],
  ["ProcessorInfo", "Manufacturer"],
  ["NetworkInfo", "NetworkPerformance"],
  ["EbsInfo", "EbsOptimizedInfo", "BaselineBandwidthInMbps"],
  ["EbsInfo", "EbsOptimizedInfo", "BaselineThroughputInMBps"],
  ["EbsInfo", "EbsOptimizedInfo", "MaximumBandwidthInMbps"],
  ["EbsInfo", "EbsOptimizedInfo", "MaximumThroughputInMBps"],
  ["EbsInfo", "EbsOptimizedInfo", "BaselineIops"],
  ["EbsInfo", "EbsOptimizedInfo", "MaximumIops"],
]

def get_nested_property(data, keys):
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return "-"
    return current


def get_ec2_instances_by(region):
  ec2_client = boto3.client('ec2', region_name = region)
  instance_types = []
  paginator = ec2_client.get_paginator('describe_instance_types')
  page_iterator = paginator.paginate()

  for page in page_iterator:
    for instance_type in page['InstanceTypes']:
      instance = {}
      for property_list in properties_to_retrieve:
        instance[".".join(property_list)] = get_nested_property(instance_type, property_list)
      instance_types.append(instance)

  return instance_types

def get_ondemand_pricing_for(instance_type, operating_system):
  client = boto3.client('pricing', region_name = 'us-east-1')

  filters = [
    {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
    {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
    {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': operating_system},
    {'Type': 'TERM_MATCH', 'Field': 'termType', 'Value': "OnDemand"}
  ]

  response = client.get_products(
    ServiceCode='AmazonEC2',
    Filters=filters
  )
  if 'PriceList' not in response:
    return {}

  price_by_region = {}
  pricing_lists = [json.loads(pricing_list) for pricing_list in response['PriceList']]
  for pricing_list in pricing_lists:
    region_code = ''
    currency = ''
    pricing_value = 0

    # Get region code
    if 'product' not in pricing_list:
      continue
    if 'attributes' not in pricing_list['product']:
      continue
    if 'regionCode' not in pricing_list['product']['attributes']:
      continue
    region_code = pricing_list['product']['attributes']['regionCode']

    if 'terms' not in pricing_list:
      continue
    if 'OnDemand' not in pricing_list['terms']:
      continue
    pricing_values = pricing_list['terms']["OnDemand"].values()
    for pricing_value in pricing_values:
      if 'priceDimensions' not in pricing_value:
        continue
      price_dimension_values = pricing_value['priceDimensions'].values()
      for price_dimension_value in price_dimension_values:
        # Validate unit for quantity as per hour unit
        if 'unit' not in price_dimension_value:
          continue
        if price_dimension_value['unit'] != "Hrs":
          continue

        if 'pricePerUnit' not in price_dimension_value:
          continue
        price_per_unit = price_dimension_value['pricePerUnit']
        if len(price_per_unit.values()) == 0:
          continue

        # Get currency and pricing value
        if 'USD' in price_per_unit and float(price_per_unit['USD']) > 0:
          currency = 'USD'
          pricing_value = float(price_per_unit['USD'])
        else:
          for price_per_unit_currency, price_per_unit_value in price_per_unit.items():
            if float(price_per_unit_value) > 0:
              currency = price_per_unit_currency
              pricing_value = float(price_per_unit_value)

      if region_code != '' and currency != '' and pricing_value > 0:
        price_by_region[region_code] = {
          'currency': currency,
          'pricing_value': pricing_value
        }

  return price_by_region

def get_3_yr_standard_reserved_pricing_for(instance_type, operating_system):
  client = boto3.client('pricing', region_name = 'us-east-1')

  filters = [
    {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
    {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
    {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': operating_system},
    {'Type': 'TERM_MATCH', 'Field': 'termType', 'Value': "Reserved"}
  ]

  response = client.get_products(
    ServiceCode='AmazonEC2',
    Filters=filters
  )
  if 'PriceList' not in response:
    return {}

  price_by_region = {}
  pricing_lists = [json.loads(pricing_list) for pricing_list in response['PriceList']]
  for pricing_list in pricing_lists:
    region_code = ''
    currency = ''
    pricing_value = 0

    # Get region code
    if 'product' not in pricing_list:
      continue
    if 'attributes' not in pricing_list['product']:
      continue
    if 'regionCode' not in pricing_list['product']['attributes']:
      continue
    region_code = pricing_list['product']['attributes']['regionCode']

    if 'terms' not in pricing_list:
      continue
    if 'Reserved' not in pricing_list['terms']:
      continue
    pricing_values = pricing_list['terms']["Reserved"].values()
    for pricing_value in pricing_values:
      # Lock to get, 3yr, standard, all upfront, payment option only
      if 'termAttributes' not in pricing_value:
        continue
      term_attributes = pricing_value['termAttributes']
      if term_attributes["LeaseContractLength"] != "3yr" or term_attributes["OfferingClass"] != "standard" or term_attributes["PurchaseOption"] != "All Upfront":
        continue

      if 'priceDimensions' not in pricing_value:
        continue
      price_dimension_values = pricing_value['priceDimensions'].values()
      for price_dimension_value in price_dimension_values:
        # Validate unit for quantity as as upfront fee
        if 'unit' not in price_dimension_value:
          continue
        if price_dimension_value['unit'] != "Quantity":
          continue

        if 'pricePerUnit' not in price_dimension_value:
          continue
        price_per_unit = price_dimension_value['pricePerUnit']
        if len(price_per_unit.values()) == 0:
          continue

        # Get currency and pricing value
        if 'USD' in price_per_unit and float(price_per_unit['USD']) > 0:
          currency = 'USD'
          pricing_value = float(price_per_unit['USD'])
        else:
          for price_per_unit_currency, price_per_unit_value in price_per_unit.items():
            if float(price_per_unit_value) > 0:
              currency = price_per_unit_currency
              pricing_value = float(price_per_unit_value)

      if region_code != '' and currency != '' and pricing_value > 0:
        price_by_region[region_code] = {
          'currency': currency,
          'pricing_value': pricing_value
        }

  return price_by_region
