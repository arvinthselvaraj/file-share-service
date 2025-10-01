import re
import uuid
from datetime import datetime, timezone
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from botocore.exceptions import ClientError
from app import config
from app.dependencies import s3, table
from app.utils.hashing import compute_sha256_and_size


def upload_file(file: UploadFile):
    """
    Function to upload file to S3 bucket and store file metadata to DynamoDb table.

    :param file: UploadFile
    :return: file ID, file name and file size
    """
    file_id = str(uuid.uuid4())
    print(f"Uploading fileId {file_id}")
    s3_key = f"uploads/{file_id}"

    try:
        size, sha256 = compute_sha256_and_size(file.file, config.MAX_BYTES)
        s3.upload_fileobj(file.file, config.BUCKET_NAME, s3_key)

        table.put_item(
            Item={
                "fileId": file_id,
                "filename": sanitize_filename(file.filename),
                "sizeBytes": size,
                "contentType": file.content_type,
                "sha256": sha256,
                "s3Key": s3_key,
                "uploadedAt": datetime.now(timezone.utc).isoformat()
            }
        )

        print(f"Upload successful. FileId {file_id},  filename {file.filename}")
        return {"id": file_id, "filename": file.filename, "size": size}

    except ValueError:
        raise HTTPException(status_code=413, detail="File size exceeds maximum limit of 20MB.")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Upload file failed due to unexpected error. {str(e)}")


def list_files():
    """
    Function to list all files metadata stored in DynamoDb table.

    :return: Files metadata
    """
    print("List all files")
    try:
        # Scan is expensive and response pagination required
        resp = table.scan(
            ProjectionExpression="fileId, filename, sizeBytes, uploadedAt"
        )
        return resp.get("Items", [])
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"List files failed due to unexpected error. {str(e)}")


def download_file(file_id: str):
    """
    Function to download a file using its unique file ID.

    :param file_id: file ID generate at the time of file upload
    :return: File to download
    """
    print(f"Downloading fileId {file_id}")
    try:
        resp = table.get_item(Key={"fileId": file_id})
        item = resp.get("Item")
        if not item:
            raise HTTPException(404, f"File not found")

        obj = s3.get_object(Bucket=config.BUCKET_NAME, Key=item["s3Key"])
        return StreamingResponse(
            obj["Body"],
            media_type=item.get("contentType", "application/octet-stream"),
            headers={
                "Content-Disposition": f'attachment; filename="{item["filename"]}"'
            },
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Download file failed due to unexpected error. {str(e)}")


def sanitize_filename(filename: str) -> str:
    """
    Function to remove unsafe characters, allow alphanumeric, underscore, dash, dot
    :param filename: un-sanitized filename
    :return: sanitized filename
    """
    sanitized = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    return sanitized
