from fastapi import  FastAPI

app = FastAPI(title="Asset Management Intelligence API")

@app.get("/health")
def health():
    return{"status": "Ok"}