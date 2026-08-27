from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routers.auth import router as auth_router

app = FastAPI(
    title="Backend Service",
    version="0.1.0"
)

app.include_router(auth_router)


@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/db-test")
def db_test():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), version();")
        ).fetchone()

    return {
        "database": result[0],
        "version": result[1],
    }
    
