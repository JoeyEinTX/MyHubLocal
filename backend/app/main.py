from fastapi import FastAPI
from app.api import devices

app = FastAPI(title="MyHubLocal")

@app.get("/")
def root():
    return {"message": "Welcome to MyHubLocal API!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# 👇 This new line pulls in all the /devices routes
app.include_router(devices.router, prefix="/devices", tags=["Devices"])
