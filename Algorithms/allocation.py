from Primary.member import Member
from Primary.money import Money

def level_fill(values, cost):
    n = len(values)
    level = values[0]
    k = 1
    remaining = cost

    while k < n:
        gap = values[k] - level
        cost_to_raise = gap * k
        if cost_to_raise > remaining:
            break
        remaining -= cost_to_raise
        level = values[k]
        k += 1

    base = remaining // k
    extra = remaining % k
    level += base

    pays = []
    for i in range(n):
        if i < k:
            pay = level - values[i]
            if i < extra:
                pay += 1
        else:
            pay = 0
        pays.append(pay)
    return pays


def allocate_proportional(cost: Money, balances: dict[Member, Money], min_percent: float = 5.0, num_payers="all"):
    cost = cost.cents
    if cost <= 0 or len(balances) == 0:
        raise ValueError("Purchase allocation invalid, unregistered cost or payers")

    members = []
    values = []
    for member, money in balances.items():
        members.append(member)
        values.append(money.cents)

    for i in range(len(values)):
        lowest = i
        for j in range(i + 1, len(values)):
            if values[j] < values[lowest]:
                lowest = j
        values[i], values[lowest] = values[lowest], values[i]
        members[i], members[lowest] = members[lowest], members[i]

    if num_payers == "all":
        n = len(members)
    elif num_payers < 1:
        raise ValueError("At least one person has to pay")
    else:
        n = min(num_payers, len(members))

    threshold = cost * min_percent / 100
    pays = level_fill(values[:n], cost)
    while n > 1 and pays[n - 1] < threshold:
        n -= 1
        pays = level_fill(values[:n], cost)

    result = {}
    for i in range(n):
        if pays[i] > 0:
            result[members[i]] = Money(pays[i])
    return result



