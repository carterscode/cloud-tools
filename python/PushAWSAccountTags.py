"""
This script reads a CSV file containing AWS account IDs and their 
respective cmdb:env tag values. For each AWS account, it checks 
if the tag value in AWS differs from the value in the CSV. If 
there's a difference, it updates the cmdb:env tag in AWS with 
the value from the CSV. If the CSV doesn't exist, run PullAWSAccountTags.py
script first to generate the CSV then make changes there and run
this script to push up the changes.
"""
import boto3
import csv

def read_csv(filename):
    """Read the CSV file and return the data."""
    data = []
    with open(filename, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            account_id, account_name, tag_key, tag_value = row
            data.append((account_id, tag_value))
    return data

def get_env_tag_for_account(organizations_client, account_id):
    """Retrieve the 'cmdb:env' tag value for a specific AWS account."""
    try:
        response = organizations_client.list_tags_for_resource(
            ResourceId=account_id
        )
        for tag in response['Tags']:
            if tag['Key'] == 'cmdb:env':
                return tag['Value']
        return None  # Return None if 'cmdb:env' tag is not found
    except Exception as e:
        print(f"Error fetching tags for account {account_id}: {e}")
        return None

def update_tag(organizations_client, account_id, tag_value):
    """Update the 'cmdb:env' tag for a specific AWS account."""
    try:
        organizations_client.tag_resource(
            ResourceId=account_id,
            Tags=[{'Key': 'cmdb:env', 'Value': tag_value}]
        )
    except Exception as e:
        print(f"Error updating tag for account {account_id}: {e}")

def main():
    # Assuming default session uses the proper credentials
    organizations_client = boto3.client('organizations')
    
    csv_data = read_csv('aws_tags.csv')
    
    for account_id, new_tag_value in csv_data:
        current_tag_value = get_env_tag_for_account(organizations_client, account_id)

        if current_tag_value != new_tag_value:
            update_tag(organizations_client, account_id, new_tag_value)
            print(f"Updated 'cmdb:env' tag for account {account_id} to {new_tag_value}")

if __name__ == "__main__":
    main()
