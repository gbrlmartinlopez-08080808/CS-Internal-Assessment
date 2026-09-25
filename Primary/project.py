from Primary.money import Money
from Primary.member import Member
from Primary.expense import Expense

class Project:

    def __init__(self, id: str, name: str, status: str = "open"):
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
        member = Member(f"m{self.member_seq}", name)
        self.members.append(member)
        return member

    def add_expense(self, amount: Money, payer: Member, date: str, description: str, proof=None):
        if self.status == "settled":
            raise ValueError("The purchase cannot be registered, the project is closed")
        elif payer not in self.members:
            raise ValueError("The payment cannot be registered, register payer correctly")

        for expense in self.expenses:
            if proof is not None and expense.proof is not None and expense.proof.impage_hash == proof.image_hash:
                raise ValueError("This receipt has already been added")

        self.expense_seq += 1
        expense = Expense(f"e{self.expense_seq}", amount, payer, date, description, proof)
        self.expenses.append(expense)
        return expense

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

