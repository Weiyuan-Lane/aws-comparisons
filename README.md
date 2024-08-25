# AWS Comparisions (By Region)

I hacked this python codebase up to use the [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) library to ping the various AWS API for understanding service availability and pricing.

This project is not meant for production use.

## Installation

- Install docker

## Running this application

- Run the application with the following command
```
docker-compose up
```
- Shell into the container with the following command
```
docker exec -it aws-comparisons sh
```
- Run any of the following commands to generate a CSV file with the various information
```
python list_available_ec2_instance_by_region.py
python list_available_services_by_region.py
python list_ec2_instance_pricing_by_region.py
python list_saving_plans_by_region.py
```

## Data from past runs

I've added the csv files created from past run (on 25th August 2024) within this repository in the `/dist` directory, if that is what you need.

Note that the previous focus was to measure what was supported in the new `ap-southeast-5` region, and the pricing information of supported EC2 instances.
