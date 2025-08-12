from fastapi import FastAPI
from routes import router

app = FastAPI(title="CuraVia", version="1.0")

app.include_router(router)

@app.get("/")
def root():
    return {"message": "CuraVia is running"}