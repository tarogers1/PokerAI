import random
import itertools
from enum import Enum
from game import PokerGame, ActionRequest, Card


if __name__ == "__main__":
    pg = PokerGame({0: "Nikash", 1: "AI", 2: "No", 3: "fi", 4: "super"},
                   {0: 100, 1: 130, 2: 150, 3: 200, 4: 250}, (5, 10), verbose=1)
    for action_req in pg.start_game():
        if action_req[0].req == ActionRequest.NEW_ROUND:
            print("NEW ROUND")
            continue

        if action_req[0].req == ActionRequest.PREFLOP:
            print("PREFLOP")
            continue

        if action_req[0].req == ActionRequest.FLOP:
            print("FLOP")
            continue

        if action_req[0].req == ActionRequest.TURN:
            print("TURN")
            continue

        if action_req[0].req == ActionRequest.RIVER:
            print("RIVER")
            continue

        # action = input(f"Player {action_req[0].player}, {[a.req for a in action_req]} "
        #                f"{[a.info for a in action_req]}\n Your cards: {pg.player_cards[action_req[0].player]}\n")
        p = action_req[0].player

        def money_str(i):
            m = str(pg.running_bets[i])
            if pg.folded[i]:
                m = "-"
            if pg.all_ins[i]:
                m = "a"*len(str(pg.running_bets[i]))

            return m

        action = input(f"MONEY: {' '.join(['$'+str(m) for m in reversed(pg.player_money.values())])}| CARDS UP: {' '.join([str(c) for c in reversed(pg.cards_up)])}\n"
                       f"{', '.join([str(i) for i in pg.player_cards[p]])} || {' '.join([str(a.req).removeprefix('ActionRequest.') for a in action_req])}\n"
                       f"{' '.join([money_str(i) for i in reversed(range(len(pg.players)))])}"
                       f"\n{' '.join([('s' if i == pg.small_blind else ('b' if i == pg.big_blind else ' '))*len(str(pg.running_bets[i])) if i!=p else '^' for i in reversed(range(len(pg.players)))])}\n")

        d = {'call': ActionRequest.CALL, "fold": ActionRequest.FOLD,
             "raise": ActionRequest.RAISE, "check": ActionRequest.CHECK,
             "all_in": ActionRequest.ALLIN}
        rd = {v:k for k, v in d.items()}

        while action.split(" ")[0] not in [rd[a] for a in [act.req for act in action_req]]:
            action = input(f"MONEY: {' '.join(['$' + str(m) for m in reversed(pg.player_money.values())])}| CARDS UP: {' '.join([str(c) for c in reversed(pg.cards_up)])}\n"
                f"{', '.join([str(i) for i in pg.player_cards[p]])} || {' '.join([str(a.req).removeprefix('ActionRequest.') for a in action_req])}\n"
                f"{' '.join([money_str(i) for i in reversed(range(len(pg.players)))])}"
                f"\n{' '.join([('s' if i == pg.small_blind else ('b' if i == pg.big_blind else ' ')) * len(str(pg.running_bets[i])) if i != p else '^' for i in reversed(range(len(pg.players)))])}\n")
        sec = int(action.split(" ")[1]) if len(action.split(" ")) > 1 else None
        pg.make_action(d[action.split(" ")[0]], sec)
