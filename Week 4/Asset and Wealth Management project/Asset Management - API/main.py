from fastapi import  FastAPI
from routers import clients

app = FastAPI(title="Asset Management Intelligence API")

app.include_router(clients.router)

@app.get("/health")
def health():
    return{"status": "Ok"}