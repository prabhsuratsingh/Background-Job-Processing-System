from contextlib import asynccontextmanager
from uuid import UUID, uuid4
from fastapi import FastAPI, Depends, HTTPException
import redis
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.database import db
from app.database.crud import fetch_job, insert_job, update_job_status
from app.schemas.job import JobCreate, JobCreateAPI
from app.workers import celery_app
from app.workers.tasks import celery_task

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield

app = FastAPI(lifespan=lifespan)
r = redis.Redis(host='redis', port=6379, db=0)

@app.get("/health")
async def health():
    return {"Status": "Healthy"}

@app.get("/health/redis")
async def health_redis():
    try:
        r.ping()
        return {"Redis": "Healthy"}
    except redis.exceptions.ConnectionError:
        raise HTTPException(status_code=500, detail={
            "Redis": "Unhealthy",
            "Error": redis.exceptions.ConnectionError.__name__
        })

@app.get("/health/postgres")
def health_postgres(db: Session = Depends(db.get_db)):
    try:
        db.execute(text("SELECT 1"))
        db.close()
        return {"Postgres": "Healthy"}
    except OperationalError:
        raise HTTPException(status_code=500, detail={
            "Postgres": "Unhealthy",
            "Error": OperationalError.__name__
        })


@app.post("/job/create")
async def create_job(payload: JobCreateAPI, db: Session = Depends(db.get_db)):
    job_id = uuid4()

    job = JobCreate(
        id=job_id,
        status="PENDING",
        job_type=payload.job_type,
        input_data=payload.payload
    )

    insert_job(db, job)

    celery_task.delay(str(job_id))

    update_job_status(db, job_id, new_status="QUEUED")

    return {
        "job id" : job_id
    }

@app.get("/jobs/fetch/{job_id}")
def get_job(job_id: UUID, db: Session = Depends(db.get_db)):
    resp = fetch_job(db, job_id)
    return {
        "data": resp
    }


if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)