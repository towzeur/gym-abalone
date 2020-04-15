# gym-abalone

<p align="center">
    <img src="docs/project-picture.png" width=100% align="center" /></br>
    <em>Abalone + gym</em>
</p>

## Table of Contents

1. [Game-presentation](#Game-presentation)
   1. [Introduction](#Introduction)
   2. [Object of the game](#Object-of-the-game)
   3. [Gameplay](#Gameplay)
2. [Rules](#Rules)
   1. [Starting-positions ](#Starting-positions)
   2. [Permitted-moves](#Permitted-moves)
   3. [Pushing-the-opponent](#Pushing-the-opponent)
      1. [Sumito](#Sumito)
      2. [Pac](#Pac)
   4. [Forbidden-moves](#Forbidden-moves)
3. [Environments](#Environments)
   1. [Observations](#Observations)
   2. [Actions](#Actions)
   3. [Reward Function](#Reward-Function)
4. [Instalation](#Instalation)
5. [Usage](#Usage)
6. [Misc](#Misc)

## Game-presentation

https://en.wikipedia.org/wiki/Abalone_%28board_game%29

### Introduction

Abalone is an two-player abstract strategy board game.
The players have
It was designed by Michel Lalet and Laurent Lévi in 1987.
on a hexagonal board with the objective of pushing six of the opponent's marbles off the edge of the board

### Object of the game

By pushing a marble from the opponent over the edge, it is placed outside the board and the marble no longer participates. The winner is the first player to push six of the opponent's marbles out of the board.

### Gameplay

On their turn, each player may move either a single marble or Column of marbles of their own color one space.
A Column consists of two or threemarbles of the same color directly adjacent to one another in a straight line.
A marble or a column can move in any direction in an in-line move or side-step move.

## Rules

### Starting-positions 

The game starts with a starting lineup.The most popular are :
-   « Standard setup » proposed by the game's creators.
-   « Beligan setup » 

Usually this is the standard setup, but at tournaments and by advanced players one of the dozens of alternative starting setups is also used.

See all the supported [variations](https://github.com/towzeur/script/80/)

### Permitted-moves

Each turn, the current player can push up to 3 marble as long as the pushed marbles are aligned.
There is two possible directions :
-   Straight (the marbles move 'like a train with wagons')
-   Sideways (the marbles each move a square sideways, which counts as one movement).

| Moves               | Diagram                                           |
| :---:               | :---:                                             |
| An "In-line" Move: Marbles are moved as a column into a free space      | <img src="docs/rules/moves/In-line.png" width=100%>   |
| A ‘Side step’ move: Marbles are moved sideways into adjacent freespaces | <img src="docs/rules/moves/Side-step.png" width=100%> |

### Pushing-the-opponent

#### Sumito

In order to push opponent's marbles, one needs to be in one of the Sumito's situation (the numerical superiority).

| Sumito              | Diagram                                           |
| :---:               | :---:                                             |
| A "3-push-2 Sumito" | <img src="docs/rules/sumito/3vs2.png" width=100%> |
| A "3-push-1 Sumito" | <img src="docs/rules/sumito/3vs1.png" width=100%> |
| A "2-push-1 Sumito" | <img src="docs/rules/sumito/3vs1.png" width=100%> |

#### PAC

Another important rule in Abalone concerns "Pac" situations. In these situations, players can't perform Sumito moves because none of them have the numerical lead.

-	1 vs 1
-	2 vs 2
-	3 vs 3
-	4 vs 3

### Forbidden-moves

- A single marble can never pushan opposing marble.
- A side stepping column cannot push any marble.
- All marbles in a column must move in the same direction.
- Enemy marbles sandwiched between friendly marbles may not be pushed
- At any turn, no more than 3 friendly marbles can be moved, thus an opponent’s Column of three can never be pushed. A position of 4-on-3 or greater is not considered a Sumito

## Environments

<img src="docs/screenshot/00.png" width=100% align="center" /></br>

### Observations

The observations is an encoded numpy arrays of size (11, 11, 3). These arrays contain signed 8-bit integer values in the [-128, 127] range. The choice of 8-bit integer values was made because we only need a couple of integer to represents the different value of the cells. 
PLAYER : 0, 1, ...  (up to 127) 
EMPTY  : -1
VOID   : -2 
these tokens can be customised.

### Actions

The game engine uses discrete actions by default. Actions passed to the `step()` function should be numpy arrays containining two numbers between 0 and 60. These two numbers correspond to the selected cell, and the destination cell, respectively.


### Reward Function

The default reward function tries to encourage the agent to 
. 
The agent is rewarded for .

The episode is terminated if the agent gets too far outside of a drivable tile, or if the `max_steps` parameter is exceeded. 

See the `step` function in [this source file](https://github.com/towzeur/gym-abalone/blob/master/gym_abalone/envs/abalone_env.py).

## Installation

### Requirements:

- Python 3.6+
- OpenAI gym
- NumPy
- Pyglet
- 
- Keras or Tensorflow (to use the scripts in `learning/`)

All the dependencies can be installed with `pip` or `conda`:

###  Using pip

```
git clone https://github.com/towzeur/gym-abalone.git
cd gym-abalone
pip3 install -e .
```

## Usage

```python
import gym
import abalone_env

env = gym.make("abalone-v0")

done = False
while not done:
    action = ... # Your agent code here
    obs, reward, done, _ = env.step(action)
    env.render()
```

## Misc

### TODO
- [X] 15/04/20 gameengine + gamegui fully works
- [.] gym integration
- [.] random agent
- [.] reinforcement learning agent

### Milestones
- [X] 15/04/20 gameengine + gamegui fully works
- [.] gym integration
- [.] random agent
- [.] reinforcement learning agent

## Citation

Bibtex if you want to cite this repository in your publications:
```
@misc{gym_abalone,
  author = {towzeur},
  title = {Abalone Environments for OpenAI Gym},
  year = {2020},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/towzeur/gym-abalone}},
}
```
