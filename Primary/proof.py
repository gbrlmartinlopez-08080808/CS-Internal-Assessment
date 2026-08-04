from Primary.money import Money
from typing import Optional

class Proof:

    def __innit__(self, file_path: str, image_hash: str, ocr_text: str = "", extr_total: Optional[Money] = None, extr_date: Optional[str] = None, extr_payer: Optional[str] = None, status: str = "pending"):
        self.file_path = file_path
        self.image_hash = image_hash
        self.ocr_text = ocr_text
        self.extr_total = extr_total
        self.extr_date = extr_date
        self.extr_payer = extr_payer
        self.status = status