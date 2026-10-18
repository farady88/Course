from fastapi import  FastAPI
from routers import clients, funds, portfolio, knowledge, insights, agent

app = FastAPI(title="Asset Management Intelligence API")

app.include_router(clients.router)
app.include_router(funds.router)
app.include_router(portfolio.router)
app.include_router(knowledge.router)
app.include_router(insights.router)
app.include_router(agent.router)

@app.get("/health")
def health():
    return{"status": "Ok"}