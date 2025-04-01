import mimetypes
import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()


def is_video_file(file_path):
    """Check if a file is a video file based on its MIME type."""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type and mime_type.startswith('video/')


def get_s3_client(account_id, access_key_id, secret_access_key):
    """Create and return an S3 client for Cloudflare R2."""
    return boto3.client('s3', endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
                        aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)


def object_exists(s3_client, bucket_name, object_name):
    """Check if an object exists in the bucket."""
    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise


def upload_video_to_cloudflare(file_path, account_id, access_key_id, secret_access_key, bucket_name, object_name=None):
    """Upload a video file to Cloudflare R2 bucket."""
    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_client = get_s3_client(account_id, access_key_id, secret_access_key)

    # Check if file already exists
    if object_exists(s3_client, bucket_name, object_name):
        return {"success": False, "error": f"File '{object_name}' already exists in the bucket", "skipped": True}

    try:
        content_type, _ = mimetypes.guess_type(file_path)
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type

        s3_client.upload_file(file_path, bucket_name, object_name, ExtraArgs=extra_args)

        public_url = f"https://{bucket_name}.r2.dev/{object_name}"
        return {"success": True, "public_url": public_url, "object_name": object_name}
    except Exception as e:
        return {"success": False, "error": str(e)}


def download_files_from_cloudflare(local_root="./assets", account_id="", access_key_id="", secret_access_key="",
                                   bucket_name=""):
    """Download all files from Cloudflare R2 bucket to local directory."""
    if not os.path.exists(local_root):
        os.makedirs(local_root)

    s3_client = get_s3_client(account_id, access_key_id, secret_access_key)

    downloaded_count = 0
    skipped_count = 0
    failed_count = 0

    try:
        # List all objects in the bucket
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' not in page:
                continue

            for obj in page['Contents']:
                object_key = obj['Key']
                local_path = os.path.join(local_root, object_key)

                # Create directory structure if it doesn't exist
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                print(f"Downloading: {object_key}")

                try:
                    if os.path.exists(local_path):
                        # Optional: Check if file needs update based on size/date
                        print(f"Skipped '{object_key}': File already exists locally")
                        skipped_count += 1
                        continue

                    # Download the file
                    s3_client.download_file(bucket_name, object_key, local_path)
                    print(f"Downloaded '{object_key}' successfully to {local_path}")
                    downloaded_count += 1
                except Exception as e:
                    print(f"Failed to download '{object_key}': {str(e)}")
                    failed_count += 1

    except Exception as e:
        print(f"Error listing objects: {str(e)}")

    return {"downloaded": downloaded_count, "skipped": skipped_count, "failed": failed_count}


def download_all_files():
    # Credentials from environment variables
    account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID', '')
    access_key_id = os.environ.get('CLOUDFLARE_ACCESS_KEY_ID', '')
    secret_access_key = os.environ.get('CLOUDFLARE_SECRET_ACCESS_KEY', '')
    bucket_name = os.environ.get('CLOUDFLARE_BUCKET_NAME', '')

    result = download_files_from_cloudflare(
        local_root="./assets",
        account_id=account_id,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        bucket_name=bucket_name
    )

    print(f"\nSummary: {result['downloaded']} downloaded, {result['skipped']} skipped, {result['failed']} failed")


def upload_all_files():
    # Root directory for recursive upload
    root_directory = "./assets"

    # Credentials from environment variables
    account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID', '')
    access_key_id = os.environ.get('CLOUDFLARE_ACCESS_KEY_ID', '')
    secret_access_key = os.environ.get('CLOUDFLARE_SECRET_ACCESS_KEY', '')
    bucket_name = os.environ.get('CLOUDFLARE_BUCKET_NAME', '')

    if not os.path.isdir(root_directory):
        print(f"Error: Directory '{root_directory}' not found")
        return

    # Process each file in the directory
    uploaded_count = 0
    skipped_count = 0
    failed_count = 0

    # Walk through all subdirectories
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)

            # Skip non-video files
            # if not is_video_file(file_path):
            #     continue

            # Create object name based on relative path
            relative_path = os.path.relpath(file_path, root_directory)
            object_name = relative_path.replace('\\', '/')  # Ensure proper path format

            print(f"Processing: {relative_path}")
            result = upload_video_to_cloudflare(file_path=file_path, account_id=account_id, access_key_id=access_key_id,
                                                secret_access_key=secret_access_key, bucket_name=bucket_name,
                                                object_name=object_name)

            if result.get("skipped"):
                print(f"Skipped '{relative_path}': Already exists in bucket")
                skipped_count += 1
            elif result["success"]:
                print(f"Uploaded '{relative_path}' successfully: {result['public_url']}")
                uploaded_count += 1
            else:
                print(f"Failed to upload '{relative_path}': {result['error']}")
                failed_count += 1

    print(f"\nSummary: {uploaded_count} uploaded, {skipped_count} skipped, {failed_count} failed")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2 or sys.argv[1] not in ["upload", "download"]:
        print("Usage: python assets_bucket_cloudflare.py [upload|download]")
    elif sys.argv[1] == "upload":
        upload_all_files()
    elif sys.argv[1] == "download":
        download_all_files()