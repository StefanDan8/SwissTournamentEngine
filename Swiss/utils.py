import os
import random

import pandas as pd


def save_round_to_Excel(data: pd.DataFrame, filepath, sheet_name, index = True):
    if not os.path.exists(filepath):
        data.to_excel(filepath, sheet_name = sheet_name, index = index)

    else:
        with pd.ExcelWriter(filepath, engine = 'openpyxl', if_sheet_exists = 'replace', mode = 'a') as writer:
            data.to_excel(writer, sheet_name = sheet_name, index = index)

    print("DataFrame exported successfully!")


def random_pairs(num_players: int, seed: int = 42) -> list[tuple]:
    random.seed(seed)
    # consider uneven case
    indices = list(range(0, num_players))
    tuples = []
    while len(indices) > 1:
        r1 = random.randrange(0, len(indices))
        player1 = indices.pop(r1)
        r2 = random.randrange(0, len(indices))
        player2 = indices.pop(r2)
        tuples.append((player1, player2))
    return tuples
