from Match import *

player1 = Player('Carlos Magnussen', 2902.6)
player2 = Player('Aron Levonian', 2790.1)

match = Match(player1, player2)
print(player1.points)
print(player2.points)
print(match)
match.setResult(Result.WHITE)
print(match)
print(player1.points)
print(player2.points)

rematch = Match(player2, player1)
rematch.setResult(Result.DRAW)
print(match)
print(player1.points)
print(player2.points)

print(player1.opponents)
