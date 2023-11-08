# This script creates a list of AWS's public IP addresses for a specified region.
# It gets the IP's from a list published by AWS.
# It will then output the results in a format that is policy friendly.

import requests

# Download the JSON file from AWS
url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
response = requests.get(url)
data = response.json()

# Prompt the user for a region (default to "us-west-2" if not specified)
user_region = input("Enter the AWS region (default: us-west-2): ") or "us-west-2"

# Initialize a list to store matching IP prefixes
matching_ip_prefixes = []

# Loop through the prefixes and find matching entries
for prefix in data['prefixes']:
    if prefix['region'] == user_region:
        matching_ip_prefixes.append(prefix['ip_prefix'])

# Display the matching IP prefixes and count
print(f"Matching IP Prefixes for region '{user_region}':")
print("[")
for ip_prefix in matching_ip_prefixes:
    print(f'    "{ip_prefix}",')
print("]")
print(f"Number of Entries Found: {len(matching_ip_prefixes)}")
