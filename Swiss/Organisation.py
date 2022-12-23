import itertools
import operator
from enum import Enum
from typing import Final

import numpy as np

from Swiss.utils import *


# def read_players(df: pd.DataFrame) -> list:
#    return list(map(lambda x: Player(name = x[0], elo = x[1]), df.to_numpy()))


def read_players(df: pd.DataFrame) -> list:
    players = [Player(name, elo, my_id = index) for (index, (name, elo)) in enumerate(zip(df['Player'], df['elo']))]
    return players


def play_round(matches: list) -> list:
    random.seed(224)
    for match in matches:
        res = random.choice(list(Result))
        match.setResult(res)
    return matches


class Tournament:
    def __init__(self, title: str, number_of_rounds: int, path_to_spreadsheet: str):
        self.dataframe: pd.DataFrame = pd.read_excel(path_to_spreadsheet).astype({'Player': 'str', 'elo': 'float'})
        self.players: Final[list] = read_players(self.dataframe)
        self.TITLE: str = title
        self.ROUNDS = number_of_rounds
        self.path = os.path.normpath(path_to_spreadsheet)
        self.num: int = len(self.players)
        self.pairMatrix = np.zeros((self.num, self.num), dtype = bool)

    def first_round(self) -> list:
        matches: list = []
        pairings = random_pairs(self.num)
        for (white, black) in pairings:
            self.pairMatrix[white, black] = True
            self.pairMatrix[black, white] = True
            matches.append(Match(self.players[white], self.players[black]))
        return matches

    def export_to_dataframe(self, matches: list, number: int, save: bool = False) -> pd.DataFrame:
        whites = [match.white for match in matches]
        blacks = [match.black for match in matches]
        d = {'white': whites, 'result': [match.result for match in matches], 'black': blacks}
        roundDf = pd.DataFrame(data = d, index = range(1, len(whites) + 1))
        if save:
            save_round_to_Excel(data = roundDf, filepath = self.path, sheet_name = "Round {}".format(number))

        return roundDf

    def create_buckets(self) -> list[list]:
        get_score = operator.attrgetter('score')
        buckets: list[list] = [list(g) for k, g in
                               itertools.groupby(sorted(self.players, key = get_score, reverse = True), get_score)]
        return buckets

    # TODO this method

    def create_weight_matrix(self, players: list) -> np.ndarray:
        num = len(players)
        weight_matrix = np.diag([np.Inf] * num)
        for i in range(num):
            for j in range(i + 1, num):
                p1: Player = players[i]
                p2: Player = players[j]
                if self.pairMatrix[p1.id, p2.id]:
                    weight_matrix[i, j] = np.Inf
                    weight_matrix[j, i] = np.Inf
        return weight_matrix

    def standings(self) -> list:
        players = sorted(self.players.copy(), key = lambda x: x.score, reverse = True)
        for i in range(0, self.num):
            print("{}.".format(i) + str(players[i]))
        return players


class Player:
    def __init__(self, name: str, elo: float, my_id: int):
        self.id: int = my_id
        self.name: Final[str] = name
        self.elo: Final[float] = elo
        self.score: int = 0
        self.opponents: list[Player] = []
        self.color: int = 0
        self.hadWhite: bool = False

    def __str__(self):
        return self.name + " ({})".format(self.score / 10)

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
        self.white.color += 1
        self.white.hadWhite = True
        self.black.color -= 1
        self.white.hadWhite = False

    def __str__(self):
        return str(self.white) + " vs. " + str(self.black) + os.linesep + "Result: " + self.result

    def setResult(self, result: Result):
        self.result = result.value
        match result:
            case Result.WHITE:
                self.white.score += 10
            case Result.BLACK:
                self.black.score += 10
            case Result.DRAW:
                self.white.score += 5
                self.black.score += 5
            case _:
                raise ValueError("This is not a valid result")
