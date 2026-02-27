from fastapi import FastAPI
from .routers.items import router as items_router
from .routers.payment import router as payment_router
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(items_router)
app.include_router(payment_router)