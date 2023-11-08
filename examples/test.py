# standard libraries
import random

# third party libraries
import gym

# aspirion libraries
import gym_abalone


class Agents:
    @staticmethod
    def choice_random(game):
        player = game.current_player
        possible_moves = game.get_possible_moves(player, group_by_type=False)
        pos0, pos1 = random.choice(possible_moves)
        return pos0, pos1

    @staticmethod
    def choice_prioritize_random(game):
        player = game.current_player
        possible_moves = game.get_possible_moves(player, group_by_type=True)
        for move_type in ["winner", "ejected", "inline_push", "inline_move", "sidestep_move"]:
            if possible_moves[move_type]:
                pos0, pos1 = random.choice(possible_moves[move_type])
                break
        return pos0, pos1


env = gym.make("abalone-v0")
env.reset(random_player=True, random_pick=True)

NB_EPISODES = 1
for episode in range(1, NB_EPISODES + 1):
    env.reset(random_player=True, random_pick=True)
    done = False
    while not done:
        # ==== YOUR AGENT HERE ====

        action = Agents.choice_prioritize_random(env.game)

        # =========================
        obs, reward, done, info = env.step(action)  # action
        print(f"{info['turn']: <4} | {info['player_name']} | {str(info['move_type']): >16} | reward={reward: >4} ")
        env.render(fps=0.5)

    print(f"Episode {info['turn']: <4} finished after {env.game.turns_count} turns \n")
env.close()
