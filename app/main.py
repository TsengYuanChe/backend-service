from fastapi import FastAPI

app = FastAPI(
    title="Backend Service",
    version="0.1.0"
)


@app.get("/")
def root():
    return {"status": "ok"}