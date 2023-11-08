"""
This script fetches tag information (cmdb:env tag specifically) for each 
AWS account within an AWS Organization and writes this information to 
a CSV file. The resulting CSV will have columns for 'Account ID', 
'Account Name', 'Tag Key', and 'Tag Value'.
"""
import boto3
import csv

def get_all_accounts_in_organization(organizations_client):
    """Retrieve a list of all accounts in the AWS Organization."""
    accounts = []
    
    paginator = organizations_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        accounts.extend(page['Accounts'])
    
    return accounts

def get_env_tag_for_account(organizations_client, account_id):
    """Retrieve the 'cmdb:env' tag for a specific AWS account."""
    try:
        response = organizations_client.list_tags_for_resource(
            ResourceId=account_id
        )
        for tag in response['Tags']:
            if tag['Key'] == 'cmdb:env':
                return tag['Key'], tag['Value']
        return '', ''  # Return empty strings if 'cmdb:env' tag is not found
    except Exception as e:
        print(f"Error fetching tags for account {account_id}: {e}")
        return '', ''

def main():
    # Assuming default session uses the proper credentials
    organizations_client = boto3.client('organizations')
    
    accounts = get_all_accounts_in_organization(organizations_client)
    
    with open('aws_tags.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header
        csv_writer.writerow(['Account ID', 'Account Name', 'Tag Key', 'Tag Value'])

        for account in accounts:
            account_id = account['Id']
            account_name = account['Name']
            
            tag_key, tag_value = get_env_tag_for_account(organizations_client, account_id)
            csv_writer.writerow([account_id, account_name, tag_key, tag_value])

if __name__ == "__main__":
    main()
