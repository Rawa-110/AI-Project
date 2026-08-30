from pydantic import BaseModel


class TicketRequest(BaseModel):
    message: str


class TicketResponse(BaseModel):
    message: str
    department: str