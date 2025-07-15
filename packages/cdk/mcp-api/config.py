import os

UV_ENV = {
    "UV_NO_CACHE": "1",
    "UV_PYTHON": "/usr/local/bin/python",
    "UV_TOOL_DIR": "/tmp/.uv/tool",
    "UV_TOOL_BIN_DIR": "/tmp/.uv/tool/bin",
    "UV_PROJECT_ENVIRONMENT": "/tmp/.venv",
    "npm_config_cache": "/tmp/.npm",
    "AWS_REGION": os.environ["AWS_REGION"],
    "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
    "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
    "AWS_SESSION_TOKEN": os.environ["AWS_SESSION_TOKEN"],
}

WORKSPACE_DIR = "/tmp/ws"

FIXED_SYSTEM_PROMPT = f"""## About File Output
- You are running on AWS Lambda. Therefore, when writing files, always write them under `{WORKSPACE_DIR}`.
- Similarly, if you need a workspace, please use the `{WORKSPACE_DIR}` directory. Do not ask the user about their current workspace. It's always `{WORKSPACE_DIR}`.
- Also, users cannot directly access files written under `{WORKSPACE_DIR}`. So when submitting these files to users, *always upload them to S3 using the `upload_file_to_s3_and_retrieve_s3_url` tool and provide the S3 URL*. The S3 URL must be included in the final output.
- If the output file is an image file, the S3 URL output must be in Markdown format.
"""

FILE_BUCKET = os.environ["FILE_BUCKET"]
AWS_REGION = os.environ["AWS_REGION"]