from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    file_size: int
    content_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileListResponse(BaseModel):
    total: int
    files: list[FileResponse]
