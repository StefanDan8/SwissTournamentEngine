import itertools
import operator
from enum import Enum
from typing import Final

import networkx as nx
import numpy as np

from Swiss.utils import *


def read_players(df: pd.DataFrame) -> list:
    players = [Player(name, elo, my_id = index) for (index, (name, elo)) in enumerate(zip(df['Player'], df['elo']))]
    return players


class Tournament:
    def __init__(self, title: str, number_of_rounds: int, path_to_spreadsheet: str):
        self.dataframe: pd.DataFrame = pd.read_excel(path_to_spreadsheet).astype({'Player': 'str', 'elo': 'float'})
        self.players: Final[list] = read_players(self.dataframe)
        self.TITLE: str = title
        self.ROUNDS = number_of_rounds
        self.path = os.path.normpath(path_to_spreadsheet)
        self.num: int = len(self.players)
        self.pairMatrix = np.zeros((self.num, self.num), dtype = bool)
        random.seed(224)

    def first_round(self) -> list:
        matches: list = []
        pairings = random_pairs(self.num)
        for (white, black) in pairings:
            self.pairMatrix[white, black] = True
            self.pairMatrix[black, white] = True
            matches.append(Match(self.players[white], self.players[black]))
        return matches

    def play_round(self, matches: list) -> list:
        for match in matches:
            res = random.choice(list(Result))
            match.setResult(res)
            self.pairMatrix[match.white.id, match.black.id] = True
            self.pairMatrix[match.black.id, match.white.id] = True
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

    # for now, even number of players
    # TODO own implementation
    def score_group_matching(self, players: list, floaters: int) -> list:
        n: int = len(players)
        big_constant: Final[int] = 1000
        for i in range(n):
            players[i].pos = i + 1
        B = (n - 2 * floaters) // 2
        G = nx.Graph()
        edges = []
        for i in range(n):
            for j in range(i + 1, n):
                if not self.pairMatrix[players[i].id, players[j].id]:
                    edge = (i, j, big_constant - compute_penalty(players[i], players[j], B))
                    edges.append(edge)
        G.add_weighted_edges_from(edges)
        pairings: list = sorted(nx.max_weight_matching(G))
        return pairings

    # Much more ugly, but a bit better. Still, the solution from middle should be the best
    def matching(self) -> list:
        matches_stack: list[list] = []
        buckets: list[list] = self.create_buckets()
        floating: int = 0
        for i in range(len(buckets) - 1):
            s_matches = []
            bucket = buckets[i]
            pairings = self.score_group_matching(bucket, floating)
            floating = len(bucket) - 2 * len(pairings)
            for w, b in pairings:
                s_matches.append(Match(bucket[w], bucket[b]))
            if not floating == 0:
                indices = get_floaters2(buckets[i], pairings)
                floaters = [buckets[i][j] for j in indices]
                for k in sorted(indices, reverse = True):
                    buckets[i].pop(k)
                buckets[i + 1] = floaters + buckets[i + 1]
            matches_stack.append(s_matches)
        bucket = buckets[len(buckets) - 1]
        pairings = self.score_group_matching(bucket, floating)
        s_matches = []
        for w, b in pairings:
            s_matches.append(Match(bucket[w], bucket[b]))
        floating = len(bucket) - 2 * len(pairings)
        if floating == 0:
            matches_stack.append(s_matches)
        else:
            s_matches = []
            i = len(buckets) - 1
            bucket = buckets[i]
            floating = 0
            while True:
                i = i - 1
                if i < 0:
                    print("Error: invalid matching!")
                    return []
                matches_stack.pop()
                bucket = bucket + buckets[i]
                pairings = self.score_group_matching(bucket, floating)
                floating = len(bucket) - 2 * len(pairings)
                if floating == 0:
                    break
            for w, b in pairings:
                s_matches.append(Match(bucket[w], bucket[b]))
            matches_stack.append(s_matches)
        matches = [match for r in matches_stack for match in r]
        return matches

    def standings(self) -> list:
        players = sorted(self.players.copy(), key = lambda x: x.score, reverse = True)
        for i in range(0, self.num):
            print("{}.".format(i) + str(players[i]))
        return players


class Player:
    def __init__(self, name: str, elo: float, my_id: int):
        self.pos: int = 0
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


def compute_penalty(p1: Player, p2: Player, B: int) -> int:
    sij: int = abs(p1.score - p2.score)
    oij: int = 0 if sij == 0 else 25 * sij * abs(p1.pos - p2.pos) - 500
    nij: int = 10 * (p1.pos + p2.pos)
    p: int = min(abs(p1.color), abs(p2.color))
    cij: int = 25 * 8 ** p if p1.color * p2.color > 0 else 0
    # TODO color penalty for -2 on p2 or 2 on p1
    hij: int = (B - abs(p1.pos - p2.pos)) ** 2 if sij == 0 else 0
    return oij + nij + cij + hij


def get_floaters2(players: list, pairings: list[tuple]) -> list:
    k = list(range(0, len(players)))
    l: list = sorted([item for t in pairings for item in t], reverse = True)
    for i in l:
        k.pop(i)
    return k


def get_floaters(players: list, pairings: list[tuple]) -> list:
    floaters: list = players.copy()
    l: list = sorted([item for t in pairings for item in t], reverse = True)
    for i in l:
        floaters.pop(i)
    return floaters


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
