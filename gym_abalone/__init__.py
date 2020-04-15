from gym.envs.registration import register

register(
    id='abalone-v0',
    entry_point='gym_abalone.envs:AbaloneEnv',
)
register(
    id='abalone-extrahard-v0',
    entry_point='gym_abalone.envs:AbaloneExtraHardEnv',
)