from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.items import router as items_router
from app.routers.orders import router as orders_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(items_router)
app.include_router(orders_router)
