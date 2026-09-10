from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="Log Monitoring & Error Detection System",
    description="Backend API for monitoring, detecting and analyzing application logs.",
    version="1.0.0"
)


app.include_router(router)