import re
import hashlib

import pytesseract
from PIL import Image

from Primary.money import Money
from Primary.proof import Proof

def file_hash(image_path: str):
    with open(image_path, "rb") as file:
        return (hashlib.sha256(file.read()).hexdigest())

def read_receipt(image_path: str):
    image = None
    try:
        image_hash = file_hash(image_path)
        image = Image.open(image_path)
        raw_text = pytesseract.image_to_string(image)
    except (FileNotFoundError, pytesseract.TesseractNotFoundError, OSError, pytesseract.TesseractError):
        raise ValueError("The receipt file could not be found, or could not be parsed, please enter details manually")
    finally:
        if image is not None:
            image.close()

    total, date, merchant = parse_receipt_text(raw_text)
    if total is None:
        raise ValueError("Total could not be found, please enter details manually")

    return Proof(
        file_path = image_path,
        image_hash = image_hash,
        ocr_text = raw_text,
        extr_total = total,
        extr_date = date,
        status = "scanned"
    )

def parse_receipt_text(raw_text: str):

    amount_pattern = r"(?<![\d.,])\d+[.,]\d{2}(?!\d|[.,]\d)"
    date_pattern = r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4}|\d{2})\b"

    lines = []
    for line in raw_text.splitlines():
        if line.strip() != "":
            lines.append(line.strip())

    date = None
    for line in lines:
        match = re.search(date_pattern, line)
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = match.group(3)

            if len(year) == 2:
                year = "20" + year
            if 1 <= day <= 31 and 1 <= month <= 12:
                date = f"{year}-{month:02d}-{day:02d}"
                break

    total = None
    for line in lines:
        upper = line.upper()
        if "TOTAL" in upper and "SUBTOTAL" not in upper:
            for text in re.findall(amount_pattern, line):
                amount = Money.from_display(text.replce(",", "."))
                if amount.cents > 0:
                    if total is None or amount.cents > total.cents:
                        total = amount

    return (total, date)

