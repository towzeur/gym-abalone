import gym

class AbaloneExtraHardEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(AbaloneExtraHardEnv, self).__init__()

    def step(self, action):
        pass

    def reset(self):
        pass

    def render(self, mode='human'):
        pass
    
    def close(self):
        pass
