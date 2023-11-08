"""
Get-AWS-Resources-ByName

Example:

python Get-AWS-Resources-ByName.py --tag_key Name --tag_value Uw2DwWb012

"""

import boto3
import json
import argparse

def get_resource_by_tag(client, tag_key, tag_value, resource_type='AWS::EC2::Instance', account_id=None, region=None, scope='foac-aggregator'):
    tag_value_upper = tag_value.upper()

    query = f"SELECT *, tags, configuration, relationships WHERE resourceType = '{resource_type}' AND tags.key = '{tag_key}' AND tags.value = '{tag_value_upper}'"
    if account_id:
        query += f" AND accountId = '{account_id}'"
    if region:
        query += f" AND awsRegion = '{region}'"

    response = client.select_aggregate_resource_config(
        ConfigurationAggregatorName=scope,
        Expression=query,
    )

    return response['Results']

def get_account_name(org_client, account_id):
    paginator = org_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        for account in page['Accounts']:
            if account['Id'] == account_id:
                return account['Name']
    return None  # If no match is found

def extract_tag_value(tags, target_key):
    for tag in tags:
        if tag['key'] == target_key:
            return tag['value']
    return 'Not found'  # If the target key is not in the tags

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Query AWS Config for resources by tag')
    parser.add_argument('--tag_key', required=True, help='Tag key to filter by')
    parser.add_argument('--tag_value', required=True, help='Tag value to filter by')
    parser.add_argument('--resource_type', default='AWS::EC2::Instance', help='Resource type to filter by. Default is AWS::EC2::Instance.')
    parser.add_argument('--account_id', help='AWS account ID to filter by')
    parser.add_argument('--region', help='AWS region to filter by')
    parser.add_argument('--scope', default='foac-aggregator', help='Configuration aggregator name. Default is foac-aggregator.')
    parser.add_argument('--aws_profile', default='AWS-UFG', help='AWS CLI profile name to use. Default is AWS-UFG.')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.aws_profile)
    client = session.client('config', region_name='us-east-1')  # Specify your region as necessary
    org_client = session.client('organizations')  # Assumes organizations access is in the same region

    results = get_resource_by_tag(client, args.tag_key, args.tag_value, args.resource_type, args.account_id, args.region, args.scope)

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



