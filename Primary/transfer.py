from Primary.member import Member
from Primary.money import Money


class Transfer:

    def __init__(self, from_member: Member, to_member: Member, amount: Money):
        self.from_member = from_member
        self.to_member = to_member
        self.amount = amount

    def __repr__(self):
        return f"Transfer from {self.from_member.name} to {self.to_member.name}: {self.amount.to_display()}"