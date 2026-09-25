class Member:

    def __init__ (self, id: str, name: str):
        self.id = id
        self.name = name
        if name.strip() == "":
            raise ValueError("A member needs a name")


