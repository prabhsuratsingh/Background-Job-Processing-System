from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
import redis
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from database import db

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

if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)