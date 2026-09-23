from Primary.member import Member
from Primary.money import Money
from Primary.transfer import Transfer
from itertools import permutations

def sort_parallel_settle(debtors: dict[Member, Money], creditors: dict[Member, Money]):

    abs_val_d_cents = []
    d_members = []
    for member, money in debtors.items():
        if money.cents != 0:
            d_members.append(member)
            cents = money.cents
            if cents < 0:
                cents = -cents
            abs_val_d_cents.append(cents)

    c_cents = []
    c_members = []
    for member, money in creditors.items():
        if money.cents != 0:
            c_members.append(member)
            c_cents.append(money.cents)

    for i in range(len(abs_val_d_cents)):
        for j in range(0, len(abs_val_d_cents) - i - 1):
            if abs_val_d_cents[j] < abs_val_d_cents[j+1]:
                abs_val_d_cents[j], abs_val_d_cents[j + 1] = abs_val_d_cents[j + 1], abs_val_d_cents[j]
                d_members[j], d_members[j+1] = d_members[j+1], d_members[j]

    for i in range(len(c_cents)):
        for j in range(0, len(c_cents) - i - 1):
            if c_cents[j] < c_cents[j + 1]:
                c_cents[j], c_cents[j + 1] = c_cents[j + 1], c_cents[j]
                c_members[j], c_members[j+1] = c_members[j+1], c_members[j]

    d_cents = abs_val_d_cents
    return (d_members, d_cents, c_members, c_cents)

def restore_order(cents, members):
    k = 0
    while k + 1 < len(cents) and cents[k] < cents[k+1]:
        cents[k], cents[k+1] = cents[k+1], cents[k]
        members[k],members[k+1] = members[k+1], members[k]
        k += 1

def balance_settle(debtors: dict[Member, Money], creditors: dict[Member, Money]):
    d_members, d_cents, c_members, c_cents = sort_parallel_settle(debtors, creditors)
    transfers = []

    while len(d_cents) > 0 and len(c_cents) > 0:
        max_debtor = d_members[0]
        max_debt_cents = d_cents[0]

        max_creditor = c_members[0]
        max_credit_cents = c_cents[0]

        if max_debt_cents < max_credit_cents:
            settle_cents = max_debt_cents
        else:
            settle_cents = max_credit_cents

        t = Transfer (
            from_member = max_debtor,
            to_member = max_creditor,
            amount = Money(settle_cents)
        )
        transfers.append(t)

        d_cents[0] = d_cents[0] - settle_cents
        c_cents[0] = c_cents[0] - settle_cents

        if d_cents[0] == 0:
            d_members.pop(0)
            d_cents.pop(0)

        restore_order(d_cents, d_members)
        restore_order(c_cents, c_members)

        if c_cents[0] == 0:
            c_members.pop(0)
            c_cents.pop(0)

    return (transfers)


def pair_first_settle(debtors: dict[Member, Money], creditors: dict[Member, Money]):
    d_members, d_cents, c_members, c_cents = sort_parallel_settle(debtors, creditors)
    transfers = []

    i = 0
    while i < len(d_cents):
        target_cents = d_cents[i]

        low = 0
        high = len(c_cents)-1
        match = False
        match_idx = -1

        while low <= high:
            mid = (low + high) // 2

            if c_cents[mid] == target_cents:
                match = True
                match_idx = mid
                break
            elif c_cents[mid] < target_cents:
                high = mid - 1
            else:
                low = mid + 1

        if match == True:
            t = Transfer(
                from_member = d_members[i],
                to_member = c_members[match_idx],
                amount = Money(target_cents)
            )
            transfers.append(t)

            d_members.pop(i)
            d_cents.pop(i)
            c_members.pop(match_idx)
            c_cents.pop(match_idx)

        else:
            i += 1

    rest_debtors = {}
    for i in range(len(d_members)):
        rest_debtors[d_members[i]] = Money(-d_cents[i])

    rest_creditors = {}
    for i in range(len(c_members)):
        rest_creditors[c_members[i]] = Money(c_cents[i])

    remaining_transfers = balance_settle(rest_debtors, rest_creditors)
    for t in remaining_transfers:
        transfers.append(t)

    return (transfers)

def match_in_order(d_members, d_cents, c_members, c_cents):
    d_left = list(d_cents)
    c_left = list(c_cents)
    transfers = []
    i = 0
    j = 0

    while i < len(d_left) and j < len(c_left):
        if d_left[i] < c_left[j]:
            amount = d_left[i]
        else:
            amount = c_left[j]

        t = Transfer (
            from_member = d_members[i],
            to_member = c_members[i],
            amount = Money(amount)
        )
        transfers.append(t)

        d_left[i] = d_left[i] - amount
        c_left[j] = c_left[j] - amount

        if d_left[i] == 0:
            i += 1
        if c_left[j] == 0:
            j += 1

    return (transfers)

def brute_force_settle(debtors: dict[Member, Money], creditors: dict[Member, Money]):
    d_members, d_cents, c_members, c_cents = sort_parallel_settle(debtors, creditors)
    best = None

    for d_order in permutations(range(len(d_members))):
        try_d_members = []
        try_d_cents = []
        for k in d_order:
            try_d_members.append(d_members[k])
            try_d_cents.append(d_cents[k])

        for c_order in permutations(range(len(c_members))):
            try_c_members = []
            try_c_cents = []
        for k in c_order:
            try_c_members.append(d_members[k])
            try_c_cents.append(d_cents[k])

        attempt = match_in_order(try_d_members, try_d_cents, try_c_members, try_c_cents)
        if best is None or len(attempt) < len(best):
            best = attempt

    return (best)





