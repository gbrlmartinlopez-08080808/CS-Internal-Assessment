class Member:

    def __init__ (self, id: str, name: str, weight: float = 1.0):
        self.id = id
        self.name = name
        self.weight = weight
        if name.strip() == "":
            raise ValueError("A member needs a name")


