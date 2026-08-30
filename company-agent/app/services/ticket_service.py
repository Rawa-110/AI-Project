from app.agents.classifier import classify_request


def create_ticket(message: str):

    department = classify_request(message)

    ticket = {
        "message": message,
        "department": department
    }

    return ticket