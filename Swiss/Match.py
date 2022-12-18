import os
from enum import Enum
from typing import Final

from Swiss.Player import Player


class Result(Enum):
    WHITE = "1 : 0"
    BLACK = "0 : 1"
    DRAW = "1/2 : 1/2"


class Match:
    def __init__(self, white: Player, black: Player):
        self.white: Final[Player] = white
        self.black: Final[Player] = black
        self.result = ''
        self.white.opponents.append(black)
        self.black.opponents.append(white)

    def __str__(self):
        return str(self.white) + " vs. " + str(self.black) + os.linesep + "Result: " + self.result

    def setResult(self, result: Result):
        self.result = result.value
        match result:
            case Result.WHITE:
                self.white.points += 1
            case Result.BLACK:
                self.black.points += 1
            case Result.DRAW:
                self.white.points += 0.5
                self.black.points += 0.5
            case _:
                raise ValueError("This is not a valid result")
