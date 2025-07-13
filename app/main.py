from fastapi import FastAPI
from app.routers.autotune_router import router as autotune_router
from app.logging_config import setup_logging

setup_logging()

app = FastAPI(title="PID-autotune-service")
app.include_router(autotune_router)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=7000, reload=True)
