from fastapi import FastAPI
from routers.items import router as items_router
from routers.restaurants import router as restaurants_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(restaurants_router)
