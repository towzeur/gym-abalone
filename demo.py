import gym
from env.gym_abalone.envs.gym_abalone import AbaloneEnv

#env = gym.make('abalone-v0')

env = AbaloneEnv()
env.reset()

print(env.action_space)
#> Discrete(2)
print(env.observation_space)
#> Box(4,)

#for _ in range(1000):
#    env.render()
#    env.step(env.action_space.sample()) # take a random action

env.close()
