from Primary.member import Member
from Primary.money import Money

def allocate_proportional(cost: Money, debtors: dict[Member, Money], min_percent: float = 5.0, num_payers = "max"):
    cost = cost.cents

    if cost <= 0 or len(debtors) == 0:
        raise ValueError("Purchase allocation invalid, no payers or unregistered cost")

    members = []
    caps = []
    for member, money in debtors.items():
        if money.cents < 0:
            members.append(member)
            caps.append(-money.cents)

    if len(members) == 0:
        raise ValueError("Account already balanced")

    if num_payers != "max":
        for i in range(len(caps)):
            biggest = i
            for j in range(i + 1, len(caps)):
                if caps[j] > caps[biggest]:
                    biggest = j
            caps[i], caps[biggest] = caps[biggest], caps[i]
            members[i], members[biggest] = members[biggest], members[i]

        if num_payers < len(members):
            members = members[:num_payers]
            caps = caps[:num_payers]

    n = len(members)
    shares = []
    for i in range(n):
        shares.append(0)

    remaining = cost
    active = []
    for i in range(n):
        active.append(i)

    while remaining > 0 and len(active) > 0:
        count = len(active)
        base = remaining // count
        extra = remaining % count

        assigned_this_round = 0
        still_active = []

        for k in range(count):
            i = active[k]
            round_amount = base
            if k < extra:
                round_amount = round_amount + 1

            room = caps[i] - shares[i]
            if round_amount >= room:
                give = room
            else:
                give = round_amount
                still_active.append(i)

            shares[i] = shares[i] + give
            assigned_this_round += give

        remaining = remaining - assigned_this_round
        active = still_active

        if assigned_this_round == 0:
            break

    if remaining > 0:
        base = remaining // n
        extra = remaining % n
        for i in range(n):
            add = base
            if i < extra:
                add = add + 1
            shares[i] = shares[i] + add
        remaining = 0

    threshold = cost * min_percent / 100
    result = {}
    for i in range(n):
        if shares[i] >= threshold:
            result[members[i]] = Money(shares[i])

    return (result)




