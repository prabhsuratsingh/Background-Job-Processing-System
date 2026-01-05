from uuid import UUID
from pydantic import BaseModel

class JobCreateAPI(BaseModel):
    job_type: str
    payload: dict

class JobCreate(BaseModel):
    id: UUID
    status: str
    job_type: str
    input_data: dict