import os
import re
import hashlib

import pytesseract
from PIL import Image

from Primary.money import Money
from Primary.proof import Proof

windows_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe\tesseract.exe"
if os.path.exists(windows_tesseract):
    pytesseract.pytesseract.tesseract_cmd = windows_tesseract


def file_hash(image_path: str):
    with open(image_path, "rb") as file:
        return (hashlib.sha256(file.read()).hexdigest())

def read_receipt(image_path: str):
    image_hash = file_hash(image_path)
    try:
        image = Image.open(image_path)
        raw_text = pytesseract.image_to_string(image)
    except pytesseract.TesseractNotFoundError:
        raise ValueError("Tesseract (OCR parsing software) is not installed, so the recept cannot be read, please type the amount instead")
    except (OSError, pytesseract.TesseractError):
        raise ValueError("The receipt could not be opened or read, please type the amount instead")

    for psm in (3, 4):
        raw_text = pytesseract.image_to_string(image, config=f"--psm {psm}")
        total, date = parse_receipt_text(raw_text)
        if total is not None:
            break

    status = "unreadable"
    if total is not None:
        status = "scanned"

    return Proof(image_path, image_hash, raw_text, total, date, status)

def parse_receipt_text(raw_text: str):

    amount_pattern = r"(?<![\d.,])\d+(?:[.,]\d{2})?(?!\d|[.,]\d)"
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
        if ("TOTAL" in upper or "AMOUNT" in upper) and "SUBTOTAL" not in upper:
            for text in re.findall(amount_pattern, line):
                amount = Money.from_display(text.replace(",", "."))
                if amount.cents > 0:
                    if total is None or amount.cents > total.cents:
                        total = amount

    return (total, date)

