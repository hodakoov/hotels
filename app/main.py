from fastapi import FastAPI

from app.bookings.router import router as booking_router
from app.users.router import router as users_router
from app.hotels.router import router as hotels_router


app = FastAPI()

app.include_router(users_router)
app.include_router(booking_router)
app.include_router(hotels_router)

