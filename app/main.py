from fastapi import FastAPI
from app.routes import auth

app = FastAPI()
app = FastAPI(title="Task & Deployment Tracker API")

app.include_router(auth.router)

@app.get("/")
def root():
    return {"status": "Task & Deployment Tracker API is running"}
