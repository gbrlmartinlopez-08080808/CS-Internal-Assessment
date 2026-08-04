class Money:

    def __init__(self, cents: int):
        self.cents = cents

    @classmethod
    def from_display(cls, amount):
        clean_amount = amount.strip().strip("€")

        if "." in clean_amount:
            euros, cents = amount.split(".", 1)
            if len(cents) == 0:
                cents = "00"
            elif len(cents) == 1:
                cents = cents + "0"
            else:
                cents = cents[0:2]
            euros = int(euros) * 100
            cents = int(cents)
            total_cents = int(euros) + int(cents)

        else:
            clean_amount = int(clean_amount)
            total_cents = clean_amount * 100

        return cls(total_cents)


    def to_display(self):
        euro = self.cents // 100
        cents = self.cents % 100
        amount = f"{euro}.{cents}€"

        return (amount)


    def add(self, other):
        self.cents = self.cents + other.cents
        return Money(self.cents)

    def __add__(self, other):
        return (self.add(other))


    def even_split(self, n):
        share = self.cents // n
        remainder = self.cents % n

        share_list = []
        for i in range(n):
            if i < remainder:
                share_cents = share + 1
                share_list.append(Money(share_cents))
            else:
                share_cents = share
                share_list.append(Money(share_cents))

        return (share_list)





