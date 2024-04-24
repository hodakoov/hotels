from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.bookings.router import router as booking_router
from app.users.router import router as users_router
from app.hotels.router import router as hotels_router
from app.hotels.rooms.router import router as rooms_router

from app.pages.router import router as pages_router
from app.images.router import router as images_router


app = FastAPI()

staticFiles = StaticFiles(directory="app/static")
app.mount(path="/static", app=staticFiles, name="static")

app.include_router(users_router)
app.include_router(booking_router)
app.include_router(hotels_router)
app.include_router(rooms_router)

app.include_router(pages_router)
app.include_router(images_router)
