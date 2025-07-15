import os
import boto3
from strands import tool

from config import FILE_BUCKET, AWS_REGION, WORKSPACE_DIR


session_id = None


@tool
def upload_file_to_s3_and_retrieve_s3_url(filepath: str) -> str:
    """Upload the file at /tmp/ws/* and retrieve the s3 path

    Args:
        filepath: The path to the uploading file
    """
    global session_id

    bucket = FILE_BUCKET
    region = AWS_REGION

    if not filepath.startswith(WORKSPACE_DIR):
        raise ValueError(
            f"{filepath} does not appear to be a file under the {WORKSPACE_DIR} directory. Files to be uploaded must exist under {WORKSPACE_DIR}."
        )

    filename = os.path.basename(filepath)
    key = f"mcp/{session_id}/{filename}"

    s3 = boto3.client("s3")
    s3.upload_file(filepath, bucket, key)

    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"


def set_session_id(new_session_id: str) -> None:
    global session_id
    session_id = new_session_id

