class Money:

    def __init__(self, cents: int):
        self.cents = cents
        if type(cents) != int:
            raise ValueError(f"Money must be built from whole cents")

    @classmethod
    def from_display(cls, amount):
        clean_amount = amount.strip().strip("€").strip()

        if clean_amount == "":
            raise ValueError("No amount was entered")
        if clean_amount[0] == "-":
            raise ValueError("An amount cannot be negative")

        if "." in clean_amount:
            euros, cents = clean_amount.split(".", 1)
            if len(cents) == 0:
                cents = "00"
            elif len(cents) == 1:
                cents = cents + "0"
            else:
                cents = cents[0:2]
            total_cents = int(euros) * 100 + int(cents)

        else:
            total_cents = int(clean_amount) * 100

        return cls(total_cents)


    def to_display(self):
        if self.cents < 0:
            sign = "-"
            abs_cents = -self.cents
        else:
            sign = ""
            abs_cents = self.cents

        euro = abs_cents // 100
        cents = abs_cents % 100
        amount = f"{sign}{euro}.{cents:02d}€"

        return (amount)


    def add(self, other):
        return Money(self.cents + other.cents)

    def __add__(self, other):
        return (self.add(other))


    def even_split(self, n):
        share_list = []
        if n <= 0:
            raise ValueError("Money cannot be split between zero people")
        else:
            share = self.cents // n
            remainder = self.cents % n
            for i in range(n):
                if i < remainder:
                    share_cents = share + 1
                    share_list.append(Money(share_cents))
                else:
                    share_cents = share
                    share_list.append(Money(share_cents))

            return (share_list)





