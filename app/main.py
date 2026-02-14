from fastapi import FastAPI
from app.routes import auth, projects, tasks, cicd
from app.core.dependencies import get_current_user
from app.models.user import User
from fastapi import Depends
from app.core.dependencies import require_admin

app = FastAPI()
app = FastAPI(title="Task & Deployment Tracker API")

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(cicd.router)

@app.get("/")
def root():
    return {"status": "Task & Deployment Tracker API is running"}


@app.get("/me")
async def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }

@app.get("/admin-only")
async def admin_only_route(current_user: User = Depends(require_admin)):
    return {"message": "Welcome, admin!"}