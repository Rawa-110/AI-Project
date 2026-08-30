from fastapi import APIRouter

from app.schemas.ticket import TicketRequest
from app.services.ticket_service import create_ticket

router = APIRouter()


@router.get("/")
def home():

    return {
        "status": "running"
    }


@router.post("/ticket")
def create_new_ticket(data: TicketRequest):

    ticket = create_ticket(data.message)

    return ticket