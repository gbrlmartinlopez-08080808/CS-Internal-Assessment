from Primary.member import Member
from Primary.money import Money

def allocate_proportional(item_cost: Money, debtors: dict[Member, int], min_percent: float = 5.0):
    item_cost = item_cost.cents

    if item_cost <= 0 or len(debtors) == 0:
        return ("Purchase allocation invalid")

    all_members = []
    all_debts = []
    grand_total_debt = 0

    for member, money in debtors.items():
        cents = money.cents
        if cents != 0:
            cents = -cents
            all_members.append(member)
            all_debts.append(cents)
            grand_total_debt = grand_total_debt + cents

    if grand_total_debt == 0:
        return ("Account already balanced")

    