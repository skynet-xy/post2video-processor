import argparse
import logging
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CloudflareR2")

# Load environment variables
load_dotenv()


@dataclass
class CloudflareCredentials:
    """Container for Cloudflare R2 credentials."""
    account_id: str
    access_key_id: str
    secret_access_key: str
    bucket_name: str

    @classmethod
    def from_env(cls) -> 'CloudflareCredentials':
        """Create credentials from environment variables."""
        return cls(
            account_id=os.environ.get('CLOUDFLARE_ACCOUNT_ID', ''),
            access_key_id=os.environ.get('CLOUDFLARE_ACCESS_KEY_ID', ''),
            secret_access_key=os.environ.get('CLOUDFLARE_SECRET_ACCESS_KEY', ''),
            bucket_name=os.environ.get('CLOUDFLARE_BUCKET_NAME', '')
        )


class CloudflareR2Client:
    """Client for interacting with Cloudflare R2 storage."""

    def __init__(self, credentials: CloudflareCredentials):
        """Initialize with Cloudflare R2 credentials."""
        self.credentials = credentials
        self.client = self._create_client()

    def _create_client(self):
        """Create and return a boto3 S3 client for Cloudflare R2."""
        return boto3.client(
            's3',
            endpoint_url=f'https://{self.credentials.account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=self.credentials.access_key_id,
            aws_secret_access_key=self.credentials.secret_access_key
        )

    def object_exists(self, object_name: str) -> bool:
        """Check if an object exists in the bucket."""
        try:
            self.client.head_object(Bucket=self.credentials.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Error checking if object exists: {e}")
            raise

    def list_objects(self) -> List[Dict[str, Any]]:
        """List all objects in the bucket."""
        objects = []
        try:
            paginator = self.client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.credentials.bucket_name):
                if 'Contents' in page:
                    objects.extend(page['Contents'])
        except ClientError as e:
            logger.error(f"Error listing objects: {e}")
            raise
        return objects

    def upload_file(self, file_path: Union[str, Path], object_name: Optional[str] = None) -> Dict[str, Any]:
        """Upload a file to Cloudflare R2 bucket."""
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "error": f"File '{file_path}' does not exist"}

        if object_name is None:
            object_name = str(file_path.name)

        # Check if file already exists
        if self.object_exists(object_name):
            return {"success": False, "error": f"File '{object_name}' already exists in the bucket", "skipped": True}

        try:
            content_type, _ = mimetypes.guess_type(str(file_path))
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            self.client.upload_file(str(file_path), self.credentials.bucket_name, object_name, ExtraArgs=extra_args)

            public_url = f"https://{self.credentials.bucket_name}.r2.dev/{object_name}"
            return {"success": True, "public_url": public_url, "object_name": object_name}
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return {"success": False, "error": str(e)}

    def download_file(self, object_key: str, local_path: Union[str, Path]) -> Dict[str, Any]:
        """Download a file from Cloudflare R2 bucket."""
        local_path = Path(local_path)

        try:
            # Create parent directories if they don't exist
            local_path.parent.mkdir(parents=True, exist_ok=True)

            if local_path.exists():
                return {"success": False, "error": f"File already exists at {local_path}", "skipped": True}

            self.client.download_file(self.credentials.bucket_name, object_key, str(local_path))
            return {"success": True, "local_path": str(local_path)}
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return {"success": False, "error": str(e)}


class AssetsManager:
    """Manager for handling asset uploads and downloads."""

    def __init__(self, r2_client: CloudflareR2Client, local_root: Union[str, Path] = "./assets"):
        """Initialize with R2 client and local root directory."""
        self.client = r2_client
        self.local_root = Path(local_root)

    def is_media_file(self, file_path: Union[str, Path], media_type: Optional[str] = None) -> bool:
        """Check if a file matches the specified media type."""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            return False

        if media_type is None:
            return True
        return mime_type.startswith(f'{media_type}/')

    def upload_all(self, media_filter: Optional[str] = None, recursive: bool = True) -> Dict[str, int]:
        """Upload all files from local directory to Cloudflare R2."""
        if not self.local_root.is_dir():
            logger.error(f"Directory '{self.local_root}' not found")
            return {"uploaded": 0, "skipped": 0, "failed": 0}

        uploaded = 0
        skipped = 0
        failed = 0

        # Find all files
        files_to_upload = []
        walk_iter = os.walk(self.local_root) if recursive else [(self.local_root, [], os.listdir(self.local_root))]

        for dirpath, _, filenames in walk_iter:
            for filename in filenames:
                file_path = Path(dirpath) / filename

                # Apply media filter if specified
                if media_filter and not self.is_media_file(file_path, media_filter):
                    continue

                files_to_upload.append(file_path)

        # Upload files with progress bar
        for file_path in tqdm(files_to_upload, desc="Uploading files"):
            relative_path = file_path.relative_to(self.local_root)
            object_name = str(relative_path).replace('\\', '/')

            result = self.client.upload_file(file_path, object_name)

            if result.get("skipped"):
                logger.info(f"Skipped '{relative_path}': Already exists in bucket")
                skipped += 1
            elif result["success"]:
                logger.info(f"Uploaded '{relative_path}': {result['public_url']}")
                uploaded += 1
            else:
                logger.error(f"Failed to upload '{relative_path}': {result['error']}")
                failed += 1

        return {"uploaded": uploaded, "skipped": skipped, "failed": failed}

    def download_all(self) -> Dict[str, int]:
        """Download all files from Cloudflare R2 to local directory."""
        self.local_root.mkdir(parents=True, exist_ok=True)

        downloaded = 0
        skipped = 0
        failed = 0

        try:
            objects = self.client.list_objects()

            for obj in tqdm(objects, desc="Downloading files"):
                object_key = obj['Key']
                local_path = self.local_root / object_key

                result = self.client.download_file(object_key, local_path)

                if result.get("skipped"):
                    logger.info(f"Skipped '{object_key}': File already exists locally")
                    skipped += 1
                elif result["success"]:
                    logger.info(f"Downloaded '{object_key}' to {result['local_path']}")
                    downloaded += 1
                else:
                    logger.error(f"Failed to download '{object_key}': {result['error']}")
                    failed += 1

        except Exception as e:
            logger.error(f"Error during download operation: {str(e)}")

        return {"downloaded": downloaded, "skipped": skipped, "failed": failed}


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Manage assets in Cloudflare R2 storage.')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload files to Cloudflare R2')
    upload_parser.add_argument('--media-type', choices=['video', 'image', 'audio'],
                              help='Filter files by media type')
    upload_parser.add_argument('--no-recursive', action='store_true',
                              help='Do not search subdirectories')

    # Download command
    subparsers.add_parser('download', help='Download files from Cloudflare R2')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize with credentials from environment variables
    credentials = CloudflareCredentials.from_env()
    r2_client = CloudflareR2Client(credentials)
    assets_manager = AssetsManager(r2_client)

    if args.command == 'upload':
        result = assets_manager.upload_all(
            media_filter=args.media_type,
            recursive=not args.no_recursive
        )
        logger.info(f"Upload complete: {result['uploaded']} uploaded, {result['skipped']} skipped, {result['failed']} failed")

    elif args.command == 'download':
        result = assets_manager.download_all()
        logger.info(f"Download complete: {result['downloaded']} downloaded, {result['skipped']} skipped, {result['failed']} failed")


if __name__ == "__main__":
    main()