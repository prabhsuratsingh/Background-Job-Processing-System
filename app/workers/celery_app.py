from celery.app import Celery
import os
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

celery_app = Celery("worker", broker=redis_url, backend=redis_url)

celery_app.autodiscover_tasks(["app.workers"])