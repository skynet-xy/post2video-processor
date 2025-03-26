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


def main():
    # Directory containing videos
    videos_directory = "./assets/video_templates"  # Update this path

    # Credentials from environment variables
    account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID', '')
    access_key_id = os.environ.get('CLOUDFLARE_ACCESS_KEY_ID', '')
    secret_access_key = os.environ.get('CLOUDFLARE_SECRET_ACCESS_KEY', '')
    bucket_name = os.environ.get('CLOUDFLARE_BUCKET_NAME', '')

    if not os.path.isdir(videos_directory):
        print(f"Error: Directory '{videos_directory}' not found")
        return

    s3_client = get_s3_client(account_id, access_key_id, secret_access_key)

    # Process each file in the directory
    uploaded_count = 0
    skipped_count = 0
    failed_count = 0

    for filename in os.listdir(videos_directory):
        file_path = os.path.join(videos_directory, filename)

        # Skip directories and non-video files
        if os.path.isdir(file_path) or not is_video_file(file_path):
            continue

        print(f"Processing: {filename}")
        result = upload_video_to_cloudflare(file_path=file_path, account_id=account_id, access_key_id=access_key_id,
            secret_access_key=secret_access_key, bucket_name=bucket_name, object_name=filename)

        if result.get("skipped"):
            print(f"Skipped '{filename}': Already exists in bucket")
            skipped_count += 1
        elif result["success"]:
            print(f"Uploaded '{filename}' successfully: {result['public_url']}")
            uploaded_count += 1
        else:
            print(f"Failed to upload '{filename}': {result['error']}")
            failed_count += 1

    print(f"\nSummary: {uploaded_count} uploaded, {skipped_count} skipped, {failed_count} failed")


if __name__ == "__main__":
    main()
