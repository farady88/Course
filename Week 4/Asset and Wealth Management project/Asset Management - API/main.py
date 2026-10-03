from fastapi import  FastAPI
from routers import clients, funds

app = FastAPI(title="Asset Management Intelligence API")

app.include_router(clients.router)
app.include_router(funds.router)

@app.get("/health")
def health():
    return{"status": "Ok"}