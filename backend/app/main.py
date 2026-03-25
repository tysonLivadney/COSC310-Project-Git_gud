from fastapi import FastAPI
from routers.auth import router as auth_router
from routers.restaurants import router as restaurants_router
from routers.menus import router as menus_router
from routers.menu_items import router as menu_items_router
from routers.orders import router as orders_router
from routers.location import router as location_router
from routers.order_total import router as order_total_router
from routers.payment import router as payment_router
from routers.reviews import router as reviews_router
from routers.delivery import router as delivery_router
from routers.admin import router as admin_router
from routers.notifications import router as notification_router
from routers.drivers import router as drivers_router
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(restaurants_router)
app.include_router(menus_router)
app.include_router(menu_items_router)
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(location_router)
app.include_router(payment_router)
app.include_router(reviews_router)
app.include_router(delivery_router)
app.include_router(order_total_router)
app.include_router(admin_router)
app.include_router(notification_router)
app.include_router(drivers_router)
