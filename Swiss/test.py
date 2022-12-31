# player_list = [Player(pl.Player, pl.elo) for pl in myDf.iterrows()]

from Swiss.Organisation import *

to = Tournament("titlu", 7, "../data/swissTournament.xlsx")
to.export_to_dataframe(play_round(to.first_round()), 1, True)
print(to.standings())
# print(to.pairMatrix)

to.export_to_dataframe(play_round(to.matching()), 2, True)
print(to.standings())
to.export_to_dataframe(play_round(to.matching()), 3, True)
print(to.standings())

'''
a = to.score_group_matching(buckets[0], 0)
print(a)
b = to.score_group_matching(buckets[1], 0)
G = nx.Graph()
G.add_nodes_from([1, 2, 3, 4])
G.add_weighted_edges_from([(1, 2, 10)])
n = nx.max_weight_matching(G)
li = {item for t in n for item in t}
print(n)
print(li)
print(list({1, 2, 3, 4} - li))
print(b)
pairings = [(1, 5), (2, 3), (0, 7)]
players = []
for i in range(8):
    players.append(Player("P{}".format(i), 242, i))
print(players)
print(get_floaters(players, pairings))
'''
