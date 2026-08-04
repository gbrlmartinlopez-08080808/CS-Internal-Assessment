import pytesseract
from PIL import Image
import re

def parse_receipt_cents(image_path: str):
    raw_text = pytesseract.image_to_string(Image.open(image_path))

    matches = re.findall(r'\b\d+[\.,]\d{2}\b', raw_text)
    if not matches:
        return 0

    max_cents = 0
    for match in matches:
        clean_match = match.replace(",",".")
        cents = int(float(clean_match) * 100)

        if cents > max_cents:
            max_cents = cents

    return (max_cents)