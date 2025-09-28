from fastapi import FastAPI
from app.routes import files

app = FastAPI(title="File Share Service")

# Register routes
app.include_router(files.router, prefix="/files", tags=["files"])
