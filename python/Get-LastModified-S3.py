import boto3
from botocore.exceptions import NoCredentialsError

def list_recently_modified_files(bucket_name, num_files):
    try:
        # Create an S3 client
        s3 = boto3.client('s3')

        # Get the AWS account ID
        aws_account_id = boto3.client('sts').get_caller_identity().get('Account')

        # Initialize a list to store all objects
        all_objects = []

        # Create a paginator to list all objects in the bucket
        paginator = s3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket_name)

        for page in page_iterator:
            if 'Contents' in page:
                all_objects.extend(page['Contents'])

        # Sort objects by last modified time in descending order
        all_objects.sort(key=lambda x: x['LastModified'], reverse=True)

        # Get the top 'num_files' most recently modified files
        recent_files = all_objects[:num_files]

        last_modified_files = [(obj['LastModified'].strftime("%Y-%m-%d %H:%M:%S"), obj['Key']) for obj in recent_files]

        return last_modified_files, bucket_name, aws_account_id

    except NoCredentialsError:
        print("AWS credentials not found or invalid.")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    bucket_name = input("Enter the S3 bucket name: ")
    num_files = int(input("Enter the number of files to return: "))

    last_modified_files, bucket_name, aws_account_id = list_recently_modified_files(bucket_name, num_files)

    if last_modified_files:
        print(f"Bucket Name: {bucket_name}")
        print(f"AWS Account ID: {aws_account_id}")
        print(f"Last {num_files} modified files:")
        for (last_modified_time, file_name) in last_modified_files:
            print(f"{last_modified_time} - {file_name}")
