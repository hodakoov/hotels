from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from fastapi_cache.decorator import cache

from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotelInfo, SHotel

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("/{location}")
@cache(expire=30)
async def get_hotels_by_location_and_time(
    location: str,
    date_from: date,
    date_to: date,
) -> list[SHotelInfo]:
    if date_from > date_to:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Дата заезда не может быть позже даты выезда")
    if (date_to - date_from).days > 31:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Невозможно забронировать отель сроком более месяца")
    hotels = await HotelDAO.find_all(location, date_from, date_to)
    return hotels


@router.get("/id/{hotel_id}", include_in_schema=True)
@cache(expire=30)
async def get_hotel_by_id(
    hotel_id: int,
) -> Optional[SHotel]:
    return await HotelDAO.find_one_or_none(id=hotel_id)