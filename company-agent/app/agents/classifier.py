def classify_request(message: str):

    text = message.lower()

    if "انترنت" in text:
        return "IT"

    if "كمبيوتر" in text:
        return "IT"

    if "اجازة" in text or "إجازة" in text:
        return "HR"

    if "راتب" in text:
        return "HR"

    if "فاتورة" in text:
        return "Finance"

    return "General"