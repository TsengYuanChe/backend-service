from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.website_visit import router as website_visit_router

app = FastAPI(
    title="Backend Service",
    description=(
        "A centralized backend service for personal analytics, "
        "tracking, and administration."
    ),
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(website_visit_router)

@app.get("/")
def root():
    return {"status": "ok"}
    
