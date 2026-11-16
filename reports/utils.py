import re


def phone_for_whatsapp(phone_number):
    number = re.sub(
        r"\D",
        "",
        phone_number,
    )

    if number.startswith("0"):
        number = "234" + number[1:]

    return number