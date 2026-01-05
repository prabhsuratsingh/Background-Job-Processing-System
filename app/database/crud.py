from uuid import UUID
from sqlalchemy.orm import Session

from app.schemas.job import JobCreate

from app.database import models


def insert_job(db: Session, j: JobCreate):
    job = models.JobMetadata(
        id=j.id,
        status=j.status,
        job_type=j.job_type,
        input_data=j.input_data
    )

    db.add(job)
    db.commit()

def update_job_status(db: Session, job_id: UUID, new_status: str, res: str = None, err: str = None):
    job = db.query(models.JobMetadata).filter(models.JobMetadata.id == job_id).first()
    if job:
        job.status = new_status
        if res:
            job.result = res
        if err:
            job.error = err
        db.commit()

def fetch_job(db: Session, job_id: UUID):
    return (
        db.query(models.JobMetadata)
        .filter(models.JobMetadata.id == job_id)
        .first()
    )