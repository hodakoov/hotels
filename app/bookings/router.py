from fastapi import APIRouter

router = APIRouter(prefix='/bookings', tags=['Бронирования'], )


@router.get("")
def get_bookings():
    pass


@router.get("/{booking_id}")
def get_booking_id(booking_id: int):
    return booking_id
