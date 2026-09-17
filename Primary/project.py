from Primary.money import Money
from Primary.member import Member
from Primary.expense import Expense

class Project:

    def __init__(self, name: str, status: str = "open"):
        self.name = name
        self.status = status
        self.members = []
        self.expenses = []


    def add_member(self, new_member: Member):
        if not self.status == "settled":
            for existing in self.members:
                if existing.id == new_member.id:
                    print("User has already been added")
                self.members.append(new_member)

        else:
            print("The project has been settled, and does not allow new members")


    def add_expense(self, expense: Expense):
        if not self.status == "settled":
            for member in self.members:
                if expense.payer == member:
                    self.expenses.append(expense)
        else:
            print("The porject has been settled, or user is not looged correctly, and does not allow new expenses")


    def total_spent(self):
        total_cents = 0
        for expense in self.expenses:
            total_cents += expense.amount.cents
        return Money(total_cents)


    def close(self):
        self.status = "settled"