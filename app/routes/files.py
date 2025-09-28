from fastapi import APIRouter, UploadFile, File
from app.services import file_service

router = APIRouter()


@router.post("/", status_code=201)
async def upload(file: UploadFile = File(...)):
    return file_service.upload_file(file)


@router.get("/")
def list_files():
    return file_service.list_files()


@router.get("/{file_id}")
def download(file_id: str):
    return file_service.download_file(file_id)
