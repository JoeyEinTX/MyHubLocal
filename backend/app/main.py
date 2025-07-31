from fastapi import FastAPI
from app.api import devices, telemetry, scenes

app = FastAPI(title="MyHubLocal")

@app.get("/")
def root():
    return {"message": "Welcome to MyHubLocal API!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include API routers
app.include_router(devices.router, prefix="/devices", tags=["Devices"])
app.include_router(telemetry.router, prefix="/telemetry", tags=["Telemetry"])
app.include_router(scenes.router, prefix="/scenes", tags=["Scenes"])
