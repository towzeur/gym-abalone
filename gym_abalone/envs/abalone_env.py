# third party libraries
import gym
import numpy as np
from gym import error, logger, spaces, utils
from gym.utils import seeding

# aspirion libraries
from gym_abalone.game.engine.gamelogic import AbaloneGame
from gym_abalone.game.graphics.abalonegui import AbaloneGui


class Reward:
    @staticmethod
    def method_1(observation, move_type):

        CONST_REWARDS = {
            "winner": 12,
            "ejected": 2,
            "inline_push": 0.5,
            "sidestep_move": -0.1,
            "inline_move": -0.1,
        }

        reward = CONST_REWARDS.get(move_type, 0)
        return reward


class AbaloneEnv(gym.Env):
    """
    Description:
        Abalone game environment

    Observation:
        Type: Box(61, 61)

    Actions:
        Type: Box(2)

    Reward:
        see the Reward class' methods

    Episode Termination:
        Abalone gameover (6 marbles pushed)
        Episode length is greater than max_turns.
    """

    metadata = {
        "render.modes": ["human", "terminal"],
        "video.frames_per_second": 10,
    }

    def __init__(self, render_mode="human", max_turns=200):

        super(AbaloneEnv, self).__init__()

        # Every environment comes with an action_space and an observation_space.
        # These attributes are of type Space
        self.action_space = gym.spaces.Box(0, 60, shape=(2,), dtype=np.uint8)
        self.observation_space = gym.spaces.Box(np.int8(0), np.int8(-1), shape=(11, 11), dtype=np.int8)

        self.render_mode = render_mode
        self.max_turns = max_turns

        self.game = AbaloneGame()
        self.gui = None
        self._modifications = None

        # self.reward_method = 'default'

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
        # assert self.action_space.contains(action), f"{action} ({type(action)})"

        reward = 0
        info = {
            "turn": self.game.turns_count,
            "move_type": None,
            "player": self.game.current_player,
            "player_name": ["white", "black"][self.game.current_player],
        }

        if self.done:
            logger.warn(
                "You are calling 'step()' even though this environment has already returned done = True."
                "You should always call 'reset()' once you receive 'done = True'"
                "-- any further steps are undefined behavior."
            )
        else:
            pos0, pos1 = action
            move_check = self.game.action_handler(pos0, pos1, return_modif=True)

            if move_check:  # if the move is a valid move
                move_type, self._modifications = move_check
                reward = Reward.method_1(self.game.board, move_type)
                # for debug
                info["move_type"] = move_type

        return self.observation, reward, self.done, info

    def reset(self, player=0, random_player=True, variant_name="classical", random_pick=False):
        self.game.reset(player=player, random_player=random_player, variant_name=variant_name, random_pick=random_pick)
        if self.render_mode == "human" and self.gui:
            self.gui.reset()
        return self.observation

    def render(self, fps=None):
        if self.render_mode == "human":
            if self.gui is None:
                self.gui = AbaloneGui(self.game)
                self.gui.reset()
            self.gui.update(self._modifications, fps=fps)
        elif self.render_mode == "terminal":
            pass

    def close(self):
        if self.render_mode == "human" and self.gui:
            self.gui.close()

    @property
    def turns(self):
        return self.game.turns_count

    @property
    def observation(self):
        return np.copy(self.game.board)

    @property
    def done(self):
        game_over = self.game.game_over
        too_much_turn = self.game.turns_count > self.max_turns
        return game_over or too_much_turn

    @property
    def current_player(self):
        return self.game.current_player

    def get_action_mask(self):
        """
        return a action mask which as a 61*61 = 3721 numpy vector
        with 0 and 1. 0 if the action is illegal and 1 otherwise.
        """
        player = self.game.current_player
        possible_moves = self.game.get_possible_moves(player, group_by_type=False)
        possible_index = np.array([p0 * 61 + p1 for p0, p1 in possible_moves])
        action_mask = np.zeros(61**2)
        action_mask[possible_index] = np.ones(possible_index.shape)
        return action_mask
