import boto3
import csv
from datetime import datetime

# AWS credentials and region configuration
output_file = "SSO-Assignments.csv"
profile_name = "AWS-Profile-Name"
region = "us-east-1"

# Replace with your AWS SSO instance ARN
sso_instance_arn = "arn:aws:sso:::instance/ssoins-7223a388d88676e7"

# Initialize AWS SSO and SSO OIDC clients
session = boto3.Session(profile_name=profile_name, region_name=region)
sso_client = session.client('sso-admin')
sso_oidc_client = session.client('sso-oidc')

# Get the list of AWS accounts
org_client = session.client('organizations')
account_list = org_client.list_accounts()['Accounts']

# Initialize dictionaries for permission sets and principals
ps_sets = {}
principals = {}

assignments = []

# Loop through AWS accounts
account_count = 1
start_time = datetime.now()

for account in account_list:
    print(f"\rAccount {account_count} of {len(account_list)} (Assignments: {len(assignments)})",
          end='', flush=True)
    account_count += 1

    # Get permission sets provisioned to the account
    ps_list_response = sso_client.list_permission_sets_provisioned_to_account(
        InstanceArn=sso_instance_arn,
        AccountId=account['Id']
    )

    for ps in ps_list_response['PermissionSets']:
        ps_arn = ps  # ps is already the PermissionSetArn as a string
        if ps_arn not in ps_sets:
            ps_info = sso_client.describe_permission_set(
                InstanceArn=sso_instance_arn,
                PermissionSetArn=ps_arn
            )
            ps_sets[ps_arn] = ps_info['PermissionSet']['Name']

        # Get account assignments for the permission set
        assignment_list = []
        next_token = None

        while True:
            if next_token:
                assignment_response = sso_client.list_account_assignments(
                    InstanceArn=sso_instance_arn,
                    AccountId=account['Id'],
                    PermissionSetArn=ps_arn,
                    NextToken=next_token
                )
            else:
                assignment_response = sso_client.list_account_assignments(
                    InstanceArn=sso_instance_arn,
                    AccountId=account['Id'],
                    PermissionSetArn=ps_arn
                )

            assignment_list.extend(assignment_response['AccountAssignments'])
            next_token = assignment_response.get('NextToken')

            if not next_token:
                break

        # Get principal information for each assignment
        for assignment in assignment_list:
            principal_id = assignment['PrincipalId']
            principal_type = assignment['PrincipalType']
            principal_key = f"{principal_type}_{principal_id}"

            if principal_key not in principals:
                if principal_type == 'USER':
                    principal_info = sso_oidc_client.get_user(
                        IdentityStoreId=sso_instance_identity_store_id,
                        UserId=principal_id
                    )
                    principals[principal_key] = principal_info['Username']
                elif principal_type == 'GROUP':
                    principal_info = sso_oidc_client.get_group(
                        IdentityStoreId=sso_instance_identity_store_id,
                        GroupId=principal_id
                    )
                    principals[principal_key] = principal_info['DisplayName']

            assignments.append({
                'AccountName': account['Name'],
                'PermissionSet': ps_sets[ps_arn],
                'Principal': principals[principal_key],
                'Type': principal_type
            })

# Write assignments to CSV file
with open(output_file, mode='w', newline='') as csv_file:
    fieldnames = ['AccountName', 'PermissionSet', 'Principal', 'Type']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(assignments)

end_time = datetime.now()
duration = end_time - start_time

print(f"\n{len(account_list)} accounts done in {duration}. Outputting result to {output_file}")
