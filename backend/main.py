from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from devices import router as devices_router

app = FastAPI(title="MyHubLocal", version="0.1.0")

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "MyHubLocal API v0.1", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include device routes
app.include_router(devices_router, prefix="/devices", tags=["Devices"])
