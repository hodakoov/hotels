from datetime import date

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from starlette import status

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking
from app.exceptions import RoomCannotBeBooked
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("")
@cache(expire=30)
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBooking]:
    return await BookingDAO.find_all(user_id=user.id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_booking(
    # booking: SNewBooking,
    room_id: int,
    date_from: date,
    date_to: date,
    user: Users = Depends(get_current_user),
):
    booking_add = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking_add:
        raise RoomCannotBeBooked
    booking_dict = {
        "room_id": booking_add.room_id,
        "date_from": booking_add.date_from,
        "date_to": booking_add.date_to,
    }

    send_booking_confirmation_email.delay(booking_dict, user.email)
    return booking_dict


@router.delete("/{booking_id}")
async def remove_booking(
    booking_id: int,
    current_user: Users = Depends(get_current_user),
):
    await BookingDAO.delete(id=booking_id, user_id=current_user.id)
