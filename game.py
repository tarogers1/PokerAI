import random
import itertools
from enum import Enum
from card import Card
import card
from collections import Counter

# wait
class ActionRequest(Enum):
    CHECK = 1
    CALL = 2
    RAISE = 3
    FOLD = 4
    NEW_ROUND = 5
    FLOP = 6
    TURN = 7
    RIVER = 8
    PREFLOP = 9


class AReqInfo(object):
    def __init__(self, player, req, info=None):
        self.req = req
        self.player = player
        self.info = info

hands = {"High Card": 0, "Pair": 1, "Two Pair": 2, "Three of a Kind": 3, "Straight": 4, "Flush": 5, "Full House": 6,
                         "Four of a Kind": 7, "Straight Flush": 8}

class ActionDispatch(object):
    def __init__(self, req, info=None):
        self.req = req
        self.info = info


class PokerGame(object):
    @staticmethod
    def create_deck(suits=["D", "H", "S", "C"]):
        deck = []
        for suit, face in itertools.product(suits, [str(i) for i in range(2, 11)] + ["J", "Q", "K", "A"]):
            deck.append(Card(suit, face))

        return deck

    def __init__(self, players, p_money, blinds, verbose=1):
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

        self.small_blind = -1
        self.big_blind = 0
        self.all_folded = False
        self.verbose = verbose

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
            self.deck = PokerGame.create_deck()
            random.shuffle(self.deck)
            self.cards_up = []

            small_blind = (1 + small_blind) % len(self.players)
            big_blind = (1 + big_blind) % len(self.players)

            self.small_blind = small_blind
            self.big_blind = big_blind

            self.player_money[small_blind] -= self.sb
            self.player_money[big_blind] -= self.bb

            self.bet = self.bb

            bet_end = (big_blind + 1) % len(self.players)
            self.running_bets = dict(zip(self.player_money.keys(), [0 for _ in range(len(self.player_money))]))
            self.running_bets[small_blind] = self.sb
            self.running_bets[big_blind] = self.bb

            done_pre_flop = False
            last_bet = big_blind
            self.folded = dict(zip(self.player_money.keys(), [False for _ in range(len(self.player_money))]))
            player = (big_blind+1) % len(self.players)
            first_turn = True
            self.all_folded = False
            pot = 0

            self.deal_cards()
            for p, v in self.player_money.items():
                if v <= 0:
                    self.player_money[p] = -1
                    self.folded[p] = True

            yield [ActionDispatch(ActionRequest.NEW_ROUND)]

            rounds = {ActionRequest.PREFLOP: 0, ActionRequest.FLOP: 3, ActionRequest.TURN: 1, ActionRequest.RIVER: 1}
            for round_type, new_cards in rounds.items():
                if self.all_folded:
                    continue

                yield [ActionDispatch(round_type)] # ROUND
                self.all_folded = False
                if round_type != ActionRequest.PREFLOP:
                    bet_end = small_blind
                    player = small_blind

                    while (self.folded[bet_end]):
                        bet_end = (bet_end + 1) % len(self.players)
                        player = bet_end

                    first_turn = True
                    self.bet = 0
                    last_bet = 0

                for i in range(new_cards):
                    self.cards_up.append(self.deck.pop())

                for action_req in self.betting_round(player, bet_end, last_bet, first_turn):
                    yield action_req

                pot += sum(list(self.running_bets.values()))
                self.running_bets = dict(zip(self.player_money.keys(), [0 for _ in range(len(self.player_money))]))

                if self.all_folded:
                    winner = list(self.folded.keys())[list(self.folded.values()).index(False)]
                    self.player_money[winner] += pot
                    continue

            if not self.all_folded:
                winners, losers = self.flip_cards_check_win()
                for winner in winners:
                    self.player_money[winner[0]] += pot/len(winners)

                if self.verbose > 0:
                    fl = ' |'.join([f'Player {l[0]}: {" ".join(str(ncnc) for ncnc in l[1][0])}, {l[1][1]}' for l in losers])
                    fw = ' |'.join([f'Player {l[0]}: {" ".join(str(ncnc) for ncnc in l[1][0])}, {l[1][1]}' for l in winners])

                    print(f"Losers: {fl}")
                    print(f"Winners: {fw}")

    @staticmethod
    def check_individual_hand(cards):

        sorted_cards = sorted(cards, key=lambda x: x.to_value())
        card_nums = [c.to_value() for c in sorted_cards]
        card_suits = [c.suit for c in sorted_cards]

        pats = [("High Card", (hands["High Card"], max(card_nums)))]

        num_dic = dict(Counter(card_nums))
        suit_dic = dict(Counter(card_suits))

        flush = max(suit_dic.values()) >= 5

        if 14 in num_dic:
            mod_cards = [1] + card_nums

            diffs1 = [c2 - c1 for c1, c2 in zip(mod_cards[:5], mod_cards[1:-1])]
            diffs1 = [d-1 for d in diffs1]

            diffs2 = [c2 - c1 for c1, c2 in zip(mod_cards[1:-1], mod_cards[2:])]
            diffs2 = [(d - 1) != 0 for d in diffs2]

            straight1 = sum(diffs1) == 0
            straight2 = sum(diffs2) == 0


            straight = straight1 or straight2
            #if straight:
                #print(diffs1, diffs2)

            max_card = max(mod_cards[:-1]) if straight1 and not straight2 else max(card_nums)
        else:
            diffs = [c2 - c1 for c1, c2 in zip(card_nums[:-1], card_nums[1:])]
            straight = sum(diffs) == 0

            max_card = max(card_nums)

        if straight and flush:
            pats.append(("Straight Flush", (hands["Straight Flush"], max_card)))

        elif straight:
            pats.append(("Straight", (hands["Straight"], max_card)))

        elif flush:
            pats.append(("Flush", (hands["Flush"], max_card)))

        # pair derivatives
        patterns = {
            "xxxxx": "High Card",
            "PPxxx": "Pair",
            "PPPxx": "Three of a Kind",
            "PPppx": "Two Pair",
            "PPPpp": "Full House",
            "PPPPx": "Four of a Kind"
        }
        pairs = list(filter(lambda x: num_dic[x] >= 2, list(num_dic.keys())))
        for p1, p2 in itertools.product(pairs, pairs):
            M = max(num_dic[p1], num_dic[p2])
            m = min(num_dic[p1], num_dic[p2])

            if p1 != p2 and M + m > 5:
                M = num_dic[p1]
                m = 5 - M

            pat = "P" * M + "p" * m

            if p1 == p2:
                pat = "P" * M

            while len(pat) < 5:
                pat += "x"

            pats.append((patterns[pat], (hands[patterns[pat]], p1)))


        best = max(pats, key=lambda x: x[1])
        return (cards, best[0], best[1])

    @staticmethod
    def check_hand(cards):
        max_ev = max([PokerGame.check_individual_hand(combo) for combo in itertools.combinations(cards, 5)], key=lambda x: x[2])
        return max_ev

    def flip_cards_check_win(self):
        winners = sorted([(p, PokerGame.check_hand(c+self.cards_up)) for p, c in enumerate(self.player_cards.values())], key=lambda x: x[1][2], reverse=True)
        winner = winners[0]
        def_winners = [winner]
        for poss_winner in winners[1:]:
            if winner == poss_winner:
                def_winners.append(poss_winner)

        return def_winners, winners[len(def_winners):]




    def betting_round(self, player, bet_end, last_bet, first_turn):
       # print("BETTING", player, bet_end)
        done_pre_flop = False
        while not done_pre_flop:
            if player == bet_end and not first_turn:
                done_pre_flop = True
                break

            first_turn = False

            if self.folded[player]:
                player = (player + 1) % len(self.players)
                continue

            moves = [AReqInfo(player, ActionRequest.FOLD)]
            if self.running_bets[player] < self.bet:
                moves.append(AReqInfo(player, ActionRequest.CALL))
                moves.append(AReqInfo(player, ActionRequest.RAISE))
            else:
                moves.append(AReqInfo(player, ActionRequest.CHECK))
                moves.append(AReqInfo(player, ActionRequest.RAISE))

            yield moves

            action_type = self.action.req
            if action_type == ActionRequest.CHECK:
                pass

            if action_type == ActionRequest.CALL:
                self.player_money[player] -= (self.bet - self.running_bets[player])
                self.running_bets[player] = self.bet

            if action_type == ActionRequest.RAISE:
                self.player_money[player] -= (self.action.info - self.running_bets[player])
                self.running_bets[player] = self.action.info
                self.bet = self.action.info
                bet_end = player

            if action_type == ActionRequest.FOLD:
                self.folded[player] = True
                self.all_folded = False
                not_fold_count = 0
                for p, folded in self.folded.items():
                    not_fold_count += 1 if not folded else 0
                if not_fold_count == 1:
                    self.all_folded = True
                    return

            player = (player + 1) % len(self.players)

    def deal_cards(self):
        for player in self.players:
            self.player_cards[player] = [self.deck.pop(0), self.deck.pop(0)]

    def flop(self):
        self.deck.pop(0)
        self.cards_up += [self.deck.pop(0) for _ in range(3)]


if __name__ == "__main__":
    c = lambda suit, face: Card(suit, face)
    card_tests = [
        [c("H", "10"), c("S", "J"), c("C", "Q"), c("S", "K"), c("H", "10"),
         c("S", "8"), c("D", "3")],
        [c("H", "10"), c("S", "J"), c("C", "Q"), c("S", "A"), c("H", "A"),
         c("S", "8"), c("D", "3")],
        [c("H", "10"), c("S", "10"), c("C", "Q"), c("S", "A"), c("H", "A"),
         c("S", "8"), c("D", "3")]
    ]
    for h in card_tests:
        print(f"Testing {' '.join([str(c) for c in h])}")
        print(PokerGame.check_hand(h))