from Swiss.Organisation import *

player1 = Player('Carlos Magnussen', 2902.6)
player2 = Player('Aron Levonian', 2790.1)
player3 = Player('Ding Liren', 2424.2)
match1 = Match(player2, player1)
match2 = Match(player3, player2)
match3 = Match(player1, player3)

print(random_pairs(8))
# roundDf["Result"] = " "

# player_list = [Player(pl.Player, pl.elo) for pl in myDf.iterrows()]
# print(player_list[0])
