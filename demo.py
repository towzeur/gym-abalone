import gym
import random
from gym_abalone.envs.abalone_env import AbaloneEnv
import numpy as np

#env = gym.make('abalone-v0')
env = AbaloneEnv()

print(env.action_space)
#> Discrete(2)
print(env.observation_space)
#> Box(4,)


class RandomAgent:

    @staticmethod
    def choice_prioritize_random(env):
        
        player = env.game_engine.current_player
        possible_moves = env.game_engine.get_possible_moves(player, group_by_type=True)

        for move_type in ['ejected', 'inline_push', 'sidestep_move', 'inline_move']:
            if possible_moves[move_type]:
                pos0, pos1 = random.choice(possible_moves[move_type])
                break

        return np.array((pos0, pos1), dtype=np.unint8)


for episode in range(10):

    env.reset(random_player=True, random_pick=True)

    done = False
    while not done:

        action = RandomAgent.choice_prioritize_random(env)

        obs, reward, done, info = env.step(action)
        print("*******",  done)
        env.render()

    print(f"Episode finished after {env.game_engine.turns_count} turns")
    

env.close()