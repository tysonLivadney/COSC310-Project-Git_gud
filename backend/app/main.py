from fastapi import FastAPI
from routers.items import router as items_router
from routers.delivery import router as delivery_router
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(delivery_router)



