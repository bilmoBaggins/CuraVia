from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from routes import router

app = FastAPI(title="CuraVia", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/api/main")
def root():
    return {"message": "CuraVia is running", "status": status.HTTP_200_OK}
