from Match import *


class Player:
    def __init__(self, name: str, elo: float):
        self.name: Final[str] = name
        self.elo: Final[float] = elo
        self.points: float = 0
        self.opponents: list[Player] = []

    def __str__(self):
        return self.name + ", {}".format(self.elo)

    def __repr__(self):
        return str(self)

    def printInfo(self):
        print("My name is {} and I have an ELO of {}!".format(self.name, self.elo))
