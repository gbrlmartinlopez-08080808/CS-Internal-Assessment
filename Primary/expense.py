from Primary.money import Money
from Primary.member import Member
from Primary.proof import Proof
from typing import Optional

class Expense:

    def __init__(self, id: str, amount: Money, payer: Member, date: str, description: str, proof: Optional[Proof] = None):
        self.id = id
        self.amount = amount
        self.payer = payer
        self.date = date
        self.description = description
        self.proof = proof

        if amount.cents <= 0:
            raise ValueError("The expense cannot be logged correctly; amount must be greater than 0")
        elif payer is None:
            raise ValueError("The expense cannot be logger correctly; no payer is identified")


    def split_between(self, members: list[Member]):
        if len(members) == 0:
            raise ValueError(f"Expense {self.id} has nobody to split between")

        shares = self.amount.even_split(len(members))
        result = {}
        for i in range(len(members)):
            result[members[i]] = shares[i]

        return (result)