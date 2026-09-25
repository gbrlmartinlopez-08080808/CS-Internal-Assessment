from Primary.money import Money
from typing import Optional

class Proof:

    def __init__(self, file_path: str, image_hash: str, ocr_text: str = "", extr_total: Optional[Money] = None, extr_date: Optional[str] = None, status: str = "unreadable"):
        self.file_path = file_path
        self.image_hash = image_hash
        self.ocr_text = ocr_text
        self.extr_total = extr_total
        self.extr_date = extr_date
        self.status = status

