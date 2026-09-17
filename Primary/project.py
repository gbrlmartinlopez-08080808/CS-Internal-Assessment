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
        if self.status == "settled":
            print("The project has been settled, and does not allow new members")
            return

        for existing in self.members:
            if existing.id == new_member.id:
                print("User has already been added")
                return

        self.members.append(new_member)


    def add_expense(self, expense: Expense):
        if self.status == "settled":
            print("The project has been settled, and does not allow new expenses")
            return

        for member in self.members:
            if expense.payer.id == member.id:
                self.expenses.append(expense)
                return

        print("The payer is not a member of this project, so the expense was not added")


    def total_spent(self):
        total_cents = 0
        for expense in self.expenses:
            total_cents += expense.amount.cents
        return Money(total_cents)


    def close(self):
        self.status = "settled"