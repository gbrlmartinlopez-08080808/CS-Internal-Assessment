from Primary.money import Money
from Primary.member import Member
from Primary.proof import Proof
from typing import Optional

class Expense:

    def __init__(self, id: str, amount: Money, payer: Member, date: str, description: str, proof: Optional[Proof] = None, participants = None):
        self.id = id
        self.amount = amount
        self.payer = payer
        self.date = date
        self.description = description
        self.proof = proof
        self.participants = participants

        if amount.cents <= 0 or payer is None:
            raise ValueError("The expense cannot be logged correctly; it must be greater than zero, and correctly associated.")

    def split_between(self, members: list[Member]):
        if self.participants is None:
            sharers = members
        else:
            sharers = []
            for member in members:
                if member in self.participants:
                    sharers.append(member)

        if len(sharers) == 0:
            raise ValueError(f"Expense {self.id} has nobody to split between")

        shares = self.amount.even_split(len(sharers))
        result = {}
        for i in range(len(sharers)):
            result[sharers[i]] = shares[i]

        return (result)