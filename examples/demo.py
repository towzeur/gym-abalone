"""
demo of the env
"""
# standard libraries
import random

# third party libraries
import gym
import numpy as np

# aspirion libraries
from gym_abalone.envs.abalone_env import AbaloneEnv


class RandomAgent:
    @staticmethod
    def choice_prioritize_random(env):

        player = env.game.current_player
        possible_moves = env.game.get_possible_moves(player, group_by_type=True)

        for move_type in ["winner", "ejected", "inline_push", "sidestep_move", "inline_move"]:
            if possible_moves[move_type]:
                i_random = np.random.randint(len(possible_moves[move_type]))
                pos0, pos1 = possible_moves[move_type][i_random]
                break

        return (pos0, pos1)

    @staticmethod
    def choice_random(env):

        player = env.game.current_player
        possible_moves = env.game.get_possible_moves(player, group_by_type=False)

        i_random = np.random.randint(len(possible_moves))
        pos0, pos1 = possible_moves[i_random]

        return (pos0, pos1)


# env = gym.make('abalone-v0')
env = AbaloneEnv(render_mode="terminal")
print(env.action_space)
# > Discrete(2)
print(env.observation_space)
# > Box(11,11)


NB_EPISODES = 1
for episode in range(1, NB_EPISODES + 1):
    env.reset(random_player=True, random_pick=True)
    done = False
    while not done:
        action = RandomAgent.choice_prioritize_random(env)
        obs, reward, done, info = env.step(action)
        print(f"{info['turn']: <4} | {info['player_name']} | {str(info['move_type']): >16} | reward={reward: >4} ")
        env.render(fps=1)
    print(f"Episode {info['turn']: <4} finished after {env.game.turns_count} turns \n")
env.close()
