class Money:

    def __init__(self, cents: int):
        if type(cents) != int:
            raise ValueError(f"Money must be built from whole cents")
        self.cents = cents

    @classmethod
    def from_display(cls, amount):
        clean_amount = amount.strip().strip("€").strip().replace(",", ".")

        if clean_amount == "":
            raise ValueError("No amount was entered")
        elif clean_amount[0] == "-":
            raise ValueError("An amount cannot be negative")
        try:
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
        except ValueError:
            raise ValueError(f"{amount} is not an amount, type it as (euros).(cents)")
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

    def even_split(self, n):
        if n <= 0:
            raise ValueError("Money cannot be split between zero people")
        else:
            share = self.cents // n
            remainder = self.cents % n
            share_list = []
            for i in range(n):
                if i < remainder:
                    share_list.append(Money(share + 1))
                else:
                    share_list.append(Money(share))

            return (share_list)





