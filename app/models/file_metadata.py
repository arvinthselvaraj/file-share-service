from pydantic import BaseModel
from typing import Optional


class FileMetadata(BaseModel):
    fileId: str
    filename: str
    sizeBytes: int
    contentType: Optional[str] = "application/octet-stream"
    sha256: str
    uploadedAt: str
