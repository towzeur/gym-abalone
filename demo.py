import gym
import random
from gym_abalone.envs.abalone_env import AbaloneEnv
import numpy as np

class RandomAgent:

    @staticmethod
    def choice_prioritize_random(env):
        
        player = env.game.current_player
        possible_moves = env.game.get_possible_moves(player, group_by_type=True)

        for move_type in ['ejected', 'inline_push', 'sidestep_move', 'inline_move']:
            if possible_moves[move_type]:
                pos0, pos1 = random.choice(possible_moves[move_type])
                break

        return np.array((pos0, pos1), dtype=np.uint8)

    @staticmethod
    def choice_random(env):
        
        player = env.game.current_player
        possible_moves = env.game.get_possible_moves(player, group_by_type=False)

        for move_type in ['ejected', 'inline_push', 'sidestep_move', 'inline_move']:
            if possible_moves[move_type]:
                pos0, pos1 = random.choice(possible_moves[move_type])
                break

        return np.array((pos0, pos1), dtype=np.uint8)


#env = gym.make('abalone-v0')
env = AbaloneEnv()

print(env.action_space)
#> Discrete(2)
print(env.observation_space)
#> Box(4,)

NB_EPISODES = 10
for episode in range(1, NB_EPISODES+1):
    env.reset(random_player=True, random_pick=True)
    done = False
    while not done:
        action = RandomAgent.choice_prioritize_random(env)
        obs, reward, done, info = env.step(action)
        print(f"{env.turns: <4} | {info['player_name']} | {str(info['move_type']): >16} | reward={reward: >4} ")
        #env.render()
    print(f"Episode {episode: <4} finished after {env.game.turns_count} turns \n")
env.close()