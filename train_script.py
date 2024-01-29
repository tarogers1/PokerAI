import random
import itertools
from enum import Enum
from game import PokerGame, ActionRequest, Card
import tqdm


class BaseModel(object):
    def __init__(self):
        pass

    def get_action(self, game, player, actions):
        return ActionRequest.FOLD, 0

    def log_data(self, game, player, action):
        pass

    def prelog(self, game):
        # log state before action made (half-entry followed by log_data func)
        pass
class CoachDNA(object):
    def __init__(self, num_players, start_money, blinds, verbose=0):
        self.num_players = num_players
        self.start_money = start_money
        self.blinds = blinds
        self.verbose = verbose

class ModelDataCoach(object):
    def __init__(self, model: BaseModel, dna: CoachDNA):
        self.model = model
        self.dna = dna
        self.game = PokerGame({k:k for k in range(dna.num_players)}, {p:dna.start_money for p in range(dna.num_players)}, dna.blinds, dna.verbose)

    def reset_game(self, dna=None):
        dna = dna if dna is not None else self.dna
        self.game = PokerGame({k:k for k in range(dna.num_players)}, {p:dna.start_money for p in range(dna.num_players)}, dna.blinds, dna.verbose)

    def simulate_games(self, iters):
        iterations = 0
        for action_req in self.game.start_game():
            if iterations == iters:
                return

            if action_req[0].req == ActionRequest.NEW_ROUND:
                iterations += 1
                continue

            p = action_req[0].player
            action = self.model.get_action(self.game, p, [areq.req for areq in action_req])

            self.model.prelog(self.game)
            self.game.make_action(*action)
            self.model.log_data(self.game, p, action)

    def test_agents(self, test_model, rounds_per_game=100, games=100):
        models = [self.model, test_model]
        plus_minus = 0
        for _ in tqdm.tqdm(range(games)):
            self.reset_game()
            iterations = 0

            for action_req in self.game.start_game():
                if min(self.game.player_money.values()) < 0:
                    break

                if iterations >= rounds_per_game:
                    break

                if action_req[0].req == ActionRequest.NEW_ROUND:
                    iterations += 1
                    continue

                if action_req[0].req == ActionRequest.PREFLOP:
                    continue

                if action_req[0].req == ActionRequest.FLOP:
                    continue

                if action_req[0].req == ActionRequest.TURN:
                    continue

                if action_req[0].req == ActionRequest.RIVER:
                    continue

                p = action_req[0].player
                action = models[p].get_action(self.game, p, [areq.req for areq in action_req])
                self.game.make_action(*action)

              #  print(iterations, self.game.player_money, action)


            plus_minus += self.game.player_money[0] - self.game.player_money[1]

        return plus_minus/games


class RandomAgent(BaseModel):
    def __init__(self, inverse_greed=3):
        self.inverse_greed = inverse_greed

    def get_action(self, game, player, actions):
        return random.choice(actions), min(random.uniform(game.bet, game.bet+game.player_money[player]/self.inverse_greed),
                                           max(game.running_bets.values())+game.player_money[player])

if __name__ == "__main__":
    dna = CoachDNA(2, 100, (10, 5))
    coach = ModelDataCoach(RandomAgent(inverse_greed=3), dna)

    res = coach.test_agents(RandomAgent(inverse_greed=6))
    print(res)