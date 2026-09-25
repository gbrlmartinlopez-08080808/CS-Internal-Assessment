from Primary.project import Project
from Primary.member import Member
from Primary.money import Money

class Acc_balance:

    def __init__(self, project: Project):
        self.project = project

    def compute_balances(self):

        raw_balances = {}
        for member in self.project.members:
            raw_balances[member] = 0

        for expense in self.project.expenses:
            raw_balances[expense.payer] += expense.amount.cents

            shares = expense.split_between(self.project.members)
            for member, share in shares.items():
                raw_balances[member] -= share.cents

        balances = {}
        for member, cents in raw_balances.items():
            balances[member] = Money(cents)
        self.check_net_balance(balances)

        return (balances)


    def debtors(self):
        balances = self.compute_balances()

        mem_debtors = {}
        for member, amount in balances.items():
            if amount.cents < 0:
                mem_debtors[member] = amount
        return mem_debtors


    def creditors(self):
        balances = self.compute_balances()

        mem_creditors = {}
        for member, amount in balances.items():
            if amount.cents > 0:
                mem_creditors[member] = amount
        return mem_creditors

    def check_net_balance(self, balances: dict[Member, Money]):
        net_cents = 0
        for amount in balances.values():
            net_cents += amount.cents

        if net_cents != 0:
            raise ValueError(f"Zero-sum broken: balances add up to {net_cents} cents")
