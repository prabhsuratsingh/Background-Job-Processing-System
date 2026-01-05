import time
from app.database.crud import update_job_status
from app.database.db import SessionLocal
from app.workers.celery_app import celery_app

db = SessionLocal()

@celery_app.task(bind=True)
def run_job(self, job_id: str):
    print(f"Running job {job_id}")

@celery_app.task(bind=True)
def celery_task(self, job_id: str):
    update_job_status(db, job_id, new_status="RUNNING")

    try:
        # do actual work
        # result = do_work()

        time.sleep(10)

        update_job_status(
            db,
            job_id,
            new_status="SUCCESS",
            res="Celery Completed task",
        )
    except Exception as e:
        update_job_status(
            db,
            job_id,
            new_status="FAILED",
            err=str(e),
        )
        raise
