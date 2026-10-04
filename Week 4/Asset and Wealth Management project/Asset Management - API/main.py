from fastapi import  FastAPI
from routers import clients, funds, portfolio

app = FastAPI(title="Asset Management Intelligence API")

app.include_router(clients.router)
app.include_router(funds.router)
app.include_router(portfolio.router)

@app.get("/health")
def health():
    return{"status": "Ok"}