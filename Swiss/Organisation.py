from enum import Enum
from typing import Final

from Swiss.utils import *


def read_players(df: pd.DataFrame) -> list:
    return list(map(lambda x: Player(name = x[0], elo = x[1]), df.to_numpy()))


class Tournament:
    def __init__(self, title: str, number_of_rounds: int, path_to_spreadsheet: str):
        self.dataframe: pd.DataFrame = pd.read_excel(path_to_spreadsheet).astype({'Player': 'str', 'elo': 'float'})
        self.players: list = read_players(self.dataframe)
        self.TITLE: str = title
        self.ROUNDS = number_of_rounds
        self.path = os.path.normpath(path_to_spreadsheet)

    def create_round(self, matches: list, number: int, save: bool = False) -> pd.DataFrame:
        whites = [match.white for match in matches]
        blacks = [match.black for match in matches]
        d = {'white': whites, 'result': ["" for _ in range(0, len(whites))], 'black': blacks}
        roundDf = pd.DataFrame(data = d, index = range(1, len(whites) + 1))
        if save:
            save_round_to_Excel(data = roundDf, filepath = self.path, sheet_name = "Round {}".format(number))

        return roundDf


class Player:
    def __init__(self, name: str, elo: float):
        self.name: Final[str] = name
        self.elo: Final[float] = elo
        self.score: float = 0
        self.opponents: list[Player] = []

    def __str__(self):
        return self.name + "({})".format(self.score)

    def __repr__(self):
        return str(self)

    def printInfo(self):
        print("My name is {} and I have an ELO of {}!".format(self.name, self.elo))


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
                self.white.score += 1
            case Result.BLACK:
                self.black.score += 1
            case Result.DRAW:
                self.white.score += 0.5
                self.black.score += 0.5
            case _:
                raise ValueError("This is not a valid result")
