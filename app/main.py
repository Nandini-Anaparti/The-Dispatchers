from fastapi import FastAPI

from app.api.routes.restaurants import router as restaurants_router
from app.api.routes.menu_items import router as menu_items_router

from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="The Dispatchers - Food Delivery App",
    version="0.1.0"
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app.mount(
    "/frontend",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="frontend",
)

app.include_router(restaurants_router)
app.include_router(menu_items_router)

@app.get("/", response_class=FileResponse, include_in_schema=False)
def root():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/health")
def health_check():
    return {"status": "ok"}
