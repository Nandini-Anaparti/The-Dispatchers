from fastapi import FastAPI

app = FastAPI(
    title="The Dispatchers - Food Delivery App",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "The Dispatchers is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}