# player_list = [Player(pl.Player, pl.elo) for pl in myDf.iterrows()]

from Swiss.Organisation import *

to = Tournament("titlu", 7, "../data/swissTournament.xlsx")
to.export_to_dataframe(play_round(to.first_round()), 100, True)
buckets = to.create_buckets()
print(to.pairMatrix)
print(buckets[0])
print(to.create_weight_matrix(buckets[1]))
