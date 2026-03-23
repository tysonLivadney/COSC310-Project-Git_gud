from fastapi import FastAPI
#from routers.auth import router as auth_router
#from routers.items import router as items_router
#from routers.orders import router as orders_router
#from routers.menus import router as menus_router
#from routers.menu_items import router as menu_items_router
#from routers.orders import router as orders_router
#from routers.admin import router as admin_router
from routers.notifications import router as notification_router
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(notification_router)
#app.include_router(restaurants_router)
#app.include_router(menus_router)
#app.include_router(menu_items_router)
#app.include_router(auth_router)
#app.include_router(items_router)
#app.include_router(delivery_router)
#app.include_router(orders_router)
#app.include_router(admin_router)
