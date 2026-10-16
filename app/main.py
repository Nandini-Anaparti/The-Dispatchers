from fastapi import FastAPI

from app.api.routes.restaurants import router as restaurants_router
from app.api.routes.menu_items import router as menu_items_router

app = FastAPI(
    title="The Dispatchers - Food Delivery App",
    version="0.1.0"
)

app.include_router(restaurants_router)
app.include_router(menu_items_router)

@app.get("/")
def root():
    return {"message": "The Dispatchers is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
