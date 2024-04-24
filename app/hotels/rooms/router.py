from datetime import date

from app.hotels.router import router
from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.schemas import SRoomInfo


@router.get("/{hotel_id}/rooms")
async def get_rooms_by_time(
    hotel_id: int,
    date_from: date,
    date_to: date,
) -> list[SRoomInfo]:
    rooms = await RoomDAO.find_all(hotel_id, date_from, date_to)
    return rooms
