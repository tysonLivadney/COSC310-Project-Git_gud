from fastapi import FastAPI
from routers.auth import router as auth_router
from routers.items import router as items_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(items_router)
