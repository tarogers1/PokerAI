import itertools

name_to_symbol = {
    'S':   '♠',
    'D': '♦',
    'H':   '♥',
    'C':    '♣',
}
class Card(object):
    def __init__(self, suit, face):
        self.suit = suit
        self.face = face

    def __str__(self):
        return f"{name_to_symbol[self.suit]}{self.face}"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.suit, self.face))

    def to_value(self):
        return card_values[self.face]

card_values = {}
suits = ["D", "H", "S", "C"]

for j, num in enumerate([str(i) for i in range(2, 11)] + ["J", "Q", "K", "A"]):
    card_values[num] = j+2

