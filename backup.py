import random
import itertools
from enum import Enum

class ActionRequest(Enum):
    CHECK=1
    CALL=2
    RAISE=3
    FOLD=4
    NEW_ROUND=5

class AReqInfo(object):
    def __init__(self, player, req, info=None):
        self.req = req
        self.player = player
        self.info = info

class ActionDispatch(object):
    def __init__(self, req, info=None):
        self.req = req
        self.info = info
class Card(object):
    def __init__(self, suit, face):
        self.suit = suit
        self.face = face

    def __str__(self):
        return f"{self.suit}{self.face}"

    def __repr__(self):
        return f"{self.suit}{self.face}"

class PokerGame(object):
    @staticmethod
    def create_deck(suits=["D", "H", "S", "C"]):
        deck = []
        for suit, face in itertools.product(suits, [str(i) for i in range(1, 11)] + ["J", "Q", "K", "A"]):
            deck.append(Card(suit, face))

        return deck

    def __init__(self, players, p_money, blinds):
        """
        :param players: dictionary mapping player id to name
        """
        self.deck = PokerGame.create_deck()
        random.shuffle(self.deck)
        self.player_cards = {}
        self.players = players
        self.cards_up = []

        self.player_money = p_money
        self.sb, self.bb = blinds
        self.action = None

    def make_action(self, req, info):
        self.action = ActionDispatch(req, info)
    def start_game(self):
        """
        Iterator function
        :return: context of what action must be run
        """
        done = False
        small_blind = -1
        big_blind = 0
        while not done:
            small_blind = (1 + small_blind) % len(self.players)
            big_blind = (1 + big_blind) % len(self.players)

            self.player_money[small_blind] -= self.sb
            self.player_money[big_blind] -= self.bb

            self.bet = self.bb
            bet_end = (big_blind+1) % len(self.players)
            self.running_bets = dict(zip(self.player_money.keys(), [0 for _ in range(len(self.player_money))]))
            self.running_bets[small_blind] = self.sb
            self.running_bets[big_blind] = self.bb
            done_pre_flop = False
            last_bet = big_blind
            self.folded = dict(zip(self.player_money.keys(), [False for _ in range(len(self.player_money))]))
            player = big_blind
            first_turn = True

            self.deal_cards()

            yield [ActionDispatch(ActionRequest.NEW_ROUND)]

            while not done_pre_flop:
                player = (player + 1) % len(self.players)

                if player == bet_end and not first_turn:
                    done_pre_flop = True
                    continue
                first_turn = False
                if self.folded[player]:
                    continue

                moves = [AReqInfo(player, ActionRequest.FOLD)]
                if self.running_bets[player] < self.bet:
                    moves.append(AReqInfo(player, ActionRequest.CALL))
                    moves.append(AReqInfo(player, ActionRequest.RAISE))
                else:
                    moves.append(AReqInfo(player, ActionRequest.CHECK))
                    moves.append(AReqInfo(player, ActionRequest.RAISE))
                print("current bets", self.bet, self.running_bets, "\n who folded", self.folded)
                yield moves

                action_type = self.action.req
                if action_type == ActionRequest.CHECK:
                    continue

                if action_type == ActionRequest.CALL:
                    self.player_money[player] -= (self.bet - self.running_bets[player])
                    self.running_bets[player] = self.bet

                    continue

                if action_type == ActionRequest.RAISE:
                    self.player_money[player] -= (self.action.info - self.running_bets[player])
                    self.running_bets[player] = self.action.info
                    self.bet = self.action.info
                    bet_end = player
                    continue

                if action_type == ActionRequest.FOLD:
                    self.folded[player] = True
                    continue

    def deal_cards(self):
        for player in self.players:
            self.player_cards[player] = [self.deck.pop(0), self.deck.pop(0)]

    def flop(self):
        self.deck.pop(0)
        self.cards_up += [self.deck.pop(0) for _ in range(3)]

if __name__ == "__main__":
    pg = PokerGame({0: "Nikash", 1: "AI", 2: "No"}, {0: 100, 1: 100, 2: 100}, (5, 10))
    for action_req in pg.start_game():
        if action_req[0].req == ActionRequest.NEW_ROUND:
            print("NEW ROUND")
            continue

        action = input(f"Player {action_req[0].player}, {[a.req for a in action_req]} "
                       f"{[a.info for a in action_req]}\n")
        d = {'call': ActionRequest.CALL, "fold": ActionRequest.FOLD,
             "raise": ActionRequest.RAISE, "check": ActionRequest.CHECK}

        while action.split(" ")[0] not in d:
            action = input(f"Player {action_req[0].player}, {[a.req for a in action_req]} "
                           f"{[a.info for a in action_req]}\n")
        sec = int(action.split(" ")[1]) if len(action.split(" ")) > 1 else None
        pg.make_action(d[action.split(" ")[0]], sec)

