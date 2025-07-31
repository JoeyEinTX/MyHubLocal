from fastapi import FastAPI

app = FastAPI(title="MyHubLocal")

@app.get("/")
def read_root():
    return {"message": "Welcome to MyHubLocal API!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
