"""
Get-AWS-Resources-ByIP

Example:

python Get-AWS-Resources-ByIP.py 10.0.0.0

"""
import boto3
import json
import sys

def get_resource_by_private_ip(client, private_ip):
    # Query the resources based on the private IP address.
    query = f"SELECT *, tags, configuration, relationships WHERE resourceType = 'AWS::EC2::Instance' AND configuration.privateIpAddress = '{private_ip}'"

    response = client.select_aggregate_resource_config(
        ConfigurationAggregatorName='aggregator',
        Expression=query,
    )

    return response['Results']

def get_account_name(org_client, account_id):
    # Fetch the account name from AWS Organizations using the account ID.
    paginator = org_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        for account in page['Accounts']:
            if account['Id'] == account_id:
                return account['Name']
    return None  # If no match is found

def extract_tag_value(tags, target_key):
    # Extract a specific tag value from the list of tags.
    for tag in tags:
        if tag['key'] == target_key:
            return tag['value']
    return 'Not found'  # If the target key is not in the tags

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <private_ip>")
        sys.exit(1)

    private_ip = sys.argv[1]

    session = boto3.Session(profile_name='AWS-Profile')  # The profile name used here should be configured with the appropriate permissions.
    client = session.client('config', region_name='us-east-1')  # Specify the region as necessary.
    org_client = session.client('organizations')  # Organizations client for fetching account name.

    # Retrieve resources by private IP.
    results = get_resource_by_private_ip(client, private_ip)

    # Convert each JSON string in the results list to a dictionary
    formatted_results = [json.loads(result) for result in results]

    print(json.dumps(formatted_results, indent=4))

    # After printing all resources, we'll work with the first result to get additional details
    if formatted_results:
        account_info = formatted_results[0]

        # Extract and print specific tag values
        if 'tags' in account_info:
            product_owner = extract_tag_value(account_info['tags'], 'ProductOwner')
            instance_name = extract_tag_value(account_info['tags'], 'Name')

            print(f"Name: {instance_name}")
            print(f"\nProduct Owner: {product_owner}")

        # Fetch and print account name
        if 'accountId' in account_info:
            account_id = account_info['accountId']
            account_name = get_account_name(org_client, account_id)
            if account_name:
                print(f"\nAccount ID: {account_id} Account Name: {account_name}")
            else:
                print(f"\nAccount Name for ID {account_id} not found.")
