import gym
from gym import error, spaces, utils, logger
from gym.utils import seeding
import numpy as np

from gym_abalone.game.graphics.abalonegui import AbaloneGui
from gym_abalone.game.engine.gamelogic import AbaloneGame


class Reward:

    @staticmethod
    def method_1(observation, move_type):

        CONST_REWARDS = {
            'winner'        : 20,
            'ejected'       : 10, 
            'inline_push'   :  3,
            'sidestep_move' :  1, 
            'inline_move'   :  1,
        }

        reward = CONST_REWARDS.get(move_type, 0)

        return reward




class AbaloneEnv(gym.Env):
    """
    Description:
        Abalone game environment

    Observation: 
        Type: Box(4)
        Num	Observation                 Min         Max
        0	Cart Position             -4.8            4.8
        1	Cart Velocity             -Inf            Inf
        2	Pole Angle                 -24 deg        24 deg
        3	Pole Velocity At Tip      -Inf            Inf
        
    Actions:
        Type: Discrete(2)
        Num	Action
        0	Push cart to the left
        1	Push cart to the right
    
    Reward:
        Reward is 1 for every step taken, including the termination step

    Starting State:
        All observations are assigned a uniform random value in [-0.05..0.05]

    Episode Termination:
        Abalone gameover (6 marble pushed)
        Episode length is greater than 200
    """

    metadata = {'render.modes': ['human']}


    def __init__(self, max_turns=200):
        
        super(AbaloneEnv, self).__init__()

        # Every environment comes with an action_space and an observation_space. 
        # These attributes are of type Space
        self.action_space = gym.spaces.Box(0, 60, shape=(2,), dtype=np.uint8)
        self.observation_space = gym.spaces.Box(np.int8(0), np.int8(-1), shape=(11, 11), dtype=np.int8)

        self.game = AbaloneGame()
        self.max_turns = max_turns

        #self.size = None
        #self.state = None #GoGame.get_init_board(size)
        #self.reward_method = 'default'


    def step(self, action):
        """
        implementation of the classic “agent-environment loop”.

        Args:
            action (object) : the board

        Returns:
            observation (object):
            reward (float)
            done (boolean)
            info (dict)
        """
        assert self.action_space.contains(action), f"{action} ({type(action)})"

        reward = 0
        info = {
            'move_type'   : None,
            'player'      : self.game.current_player,
            'player_name' : ['white', 'black'][self.game.current_player]
        }          

        if self.done:
            logger.warn("You are calling 'step()' even though this environment has already returned done = True." 
                        "You should always call 'reset()' once you receive 'done = True'"
                        "-- any further steps are undefined behavior.")   
        else:
            pos0, pos1 = action
            move_check = self.game.action_handler(pos0, pos1, return_modif=True)

            if move_check: # if the move is a valid move
                move_type, modifications = move_check
                reward = Reward.method_1(self.game.board, move_type)
                # for debug
                info['move_type'] = move_type

        return self.observation, reward, self.done, info

    def reset(self, player=0, random_player=True, variant_name='classical', random_pick=False):
        self.game.init_game(
            player=player, random_player=random_player, 
            variant_name=variant_name, random_pick=random_pick
        )


    def render(self, mode='human'):
        pass
    
    def close(self):
        pass

    @property
    def turns(self):
        return self.game.turns_count

    @property
    def observation(self):
        return np.copy(self.game.board)

    @property
    def done(self):
        game_over =      self.game.game_over
        too_much_turn = (self.game.turns_count > self.max_turns)
        return  game_over or too_much_turn
        