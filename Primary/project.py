from Primary.money import Money
from Primary.member import Member
from Primary.expense import Expense

class Project:

    def __init__(self, id: str, members, expenses, name: str, member_seq: int, expense_seq: int, status: str = "open"):
        self.id = id
        self.name = name
        self.status = status
        self.members = []
        self.expenses = []
        self.member_seq = 0
        self.expense_seq = 0

    def add_member(self, name: str):
        if self.status == "settled":
            raise ValueError("Member cannot be added, project is closed")

        for existing in self.members:
            if existing.name.lower() == name.strip().lower():
                raise ValueError(f"{name} is already a member")

        self.member_seq += 1
        member = Member(f"m{self.member_seq}", name, 1.0)
        self.members.append(member)
        return member

    def add_expense(self, amount: Money, payer: Member, date: str, description: str, proof=None, participants=None):
        if self.status == "settled" or payer not in self.members:
            raise ValueError("The payment cannot be registered due to project closed, or payer unidentified")
        if participants is not None:
            for person in participants:
                if person not in self.members:
                    raise ValueError(f"{person.name} is not a member of this project")

        self.expense_seq += 1
        expense = Expense(f"e{self.expense_seq}", amount, payer, date, description, proof, participants)
        self.expenses.append(expense)
        return expense

    def restore_member(self, member):
        for existing in self.members:
            if existing.id == member.id:
                raise ValueError(f"Duplicate member id: {member.id}")
        self.members.append(member)
        number = int(member.id[1:])
        if number > self.member_seq:
            self.member_seq = number

    def total_spent(self):
        total_cents = 0
        for expense in self.expenses:
            total_cents += expense.amount.cents
        return Money(total_cents)

    def close(self):
        if self.status == "settled" or len(self.expenses) == 0:
            raise ValueError("The project is already settled, or is currently empty")
        else:
            self.status = "settled"

