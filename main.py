import random
import itertools
from enum import Enum
from game import PokerGame, ActionRequest, Card


if __name__ == "__main__":
    pg = PokerGame({0: "Nikash", 1: "AI", 2: "No"}, {0: 100, 1: 100, 2: 100}, (5, 10))
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
        action = input(f"MONEY: {' '.join(['$'+str(m) for m in pg.player_money.values()])}| CARDS UP: {' '.join([str(c) for c in pg.cards_up])}\n"
                       f"{', '.join([str(i) for i in pg.player_cards[p]])} || {' '.join([str(a.req).removeprefix('ActionRequest.') for a in action_req])}\n"
                       f"{' '.join([str(pg.running_bets[i]) if not pg.folded[i] else '-' for i in range(len(pg.players))])}"
                       f"\n{' '.join([('s' if i == pg.small_blind else ('b' if i == pg.big_blind else ' '))*len(str(pg.running_bets[i])) if i!=p else '^' for i in range(len(pg.players))])}\n")

        d = {'call': ActionRequest.CALL, "fold": ActionRequest.FOLD,
             "raise": ActionRequest.RAISE, "check": ActionRequest.CHECK}
        rd = {v:k for k, v in d.items()}

        while action.split(" ")[0] not in [rd[a] for a in [act.req for act in action_req]]:
            action = input(f"{', '.join([str(i) for i in pg.player_cards[p]])} || {' '.join([str(a.req).removeprefix('ActionRequest.') for a in action_req])}\n"
                       f"{' '.join([str(pg.running_bets[i]) if not pg.folded[i] else '-' for i in range(len(pg.players))])}"
                       f"\n{' '.join([' '*len(str(pg.running_bets[i])) if i!=p else '^' for i in range(len(pg.players))])}\n")
        sec = int(action.split(" ")[1]) if len(action.split(" ")) > 1 else None
        pg.make_action(d[action.split(" ")[0]], sec)