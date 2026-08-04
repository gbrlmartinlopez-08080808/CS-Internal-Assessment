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

    def split_between(self, members: list[Member]):
        shares = self.amount.even_split(len(members))
        result = {}
        for i in range(len(members)):
            result[members[i]] = shares[i]

        return (result)