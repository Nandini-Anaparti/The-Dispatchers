from fastapi import FastAPI
from app.api.routes.restaurants import router as restaurants_router
from app.api.routes.menu_items import router as menu_items_router
from app.api.routes.customers import router as customers_router
from app.api.routes.auth import router as auth_router
from app.api.routes.restaurant_owners import router as restaurant_owners_router
from app.api.routes.carts import router as carts_router
from app.api.routes.checkout import router as checkout_router
from app.api.routes.orders import router as orders_router
from app.api.routes.restaurant_orders import router as restaurant_orders_router
from pathlib import Path
from typing import Literal
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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
app.include_router(customers_router)
app.include_router(auth_router)
app.include_router(restaurant_owners_router)
app.include_router(carts_router)
app.include_router(checkout_router)
app.include_router(orders_router)
app.include_router(restaurant_orders_router)

@app.get("/", response_class=FileResponse, include_in_schema=False)
def root():
    return FileResponse(FRONTEND_DIR / "index.html")

class HealthResponse(BaseModel):
    status: Literal["ok"]


@app.get("/health")
def health_check() -> HealthResponse:
    """Report that the API is running."""
    return HealthResponse(status="ok")
