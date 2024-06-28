import gymnasium as gym
import numpy as np
import time

def get_game(game, mode):
    env = gym.make('ALE/'+str(game)+'-v5', render_mode=mode, full_action_space=False, repeat_action_probability=0.1, obs_type='rgb')
    meaning = env.unwrapped.get_action_meanings()
    actionDict = {meaning[i]: i for i in range(len(meaning))}
    print('Available actions:',actionDict)
    return env, actionDict

def print_info(obs, reward, terminated, truncated, info):
    print('reward:', reward)
    print('terminated', terminated)
    print('info', info)

all_games = ['Adventure', 'AirRaid', 'Alien', 'Amidar', 'Assault', 'Asterix', 'Asteroids', 'Atlantis', 'Atlantis2', 'Backgammon', 'BankHeist', 'BasicMath', 'BattleZone', 'BeamRider', 'Berzerk', 'Blackjack', 'Bowling', 'Boxing', 'Breakout', 'CMakeLists', 'Carnival', 'Casino', 'Centipede', 'ChopperCommand', 'CrazyClimber', 'Crossbow', 'DarkChambers', 'Defender', 'DemonAttack', 'DonkeyKong', 'DoubleDunk', 'Earthworld', 'ElevatorAction', 'Enduro', 'Entombed', 'Et', 'FishingDerby', 'FlagCapture', 'Freeway', 'Frogger', 'Frostbite', 'Galaxian', 'Gopher', 'Gravitar', 'Hangman', 'HauntedHouse', 'Hero', 'HumanCannonball', 'IceHockey', 'JamesBond', 'JourneyEscape', 'Kaboom', 'Kangaroo', 'KeystoneKapers', 'Kingkong', 'Klax', 'Koolaid', 'Krull', 'KungFuMaster', 'LaserGates', 'LostLuggage', 'MarioBros', 'MiniatureGolf', 'MontezumaRevenge', 'MrDo', 'MsPacman', 'NameThisGame', 'Othello', 'Pacman', 'Phoenix', 'Pitfall', 'Pitfall2', 'Pong', 'Pooyan', 'PrivateEye', 'QBert', 'RiverRaid', 'RoadRunner', 'RoboTank', 'Seaquest', 'SirLancelot', 'Skiing', 'Solaris', 'SpaceInvaders', 'SpaceWar', 'StarGunner', 'Superman', 'Surround', 'Tennis', 'Tetris', 'TicTacToe3d', 'TimePilot', 'Trondead', 'Turmoil', 'Tutankham', 'UpNDown', 'Venture', 'VideoCheckers', 'VideoChess', 'VideoCube', 'VideoPinball', 'WizardOfWor', 'WordZapper', 'YarsRevenge', 'Zaxxon']
paper_games = ['Seaquest', 'SpaceInvaders', 'Alien', 'Enduro']
mode = 'human' # be able to see the game
#mode = 'rgb_array'

for game in paper_games:
    env, actionDict = get_game(game, mode)
    env.reset()
    print('Playing',game)
    obs,reward, terminated, truncated, info = env.step(0)
    totalReward = 0

    while not terminated:
        action = np.random.randint(env.action_space.n)  # Random action selection
        obs, reward, terminated, truncated, info = env.step(action)
        totalReward += reward
        env.render()
        if mode == 'human':
            time.sleep(0.05) 
            print_info(obs, reward, terminated, truncated, info)
            print('total reward', totalReward)
            
    print_info(obs, reward, terminated, truncated, info)
    print('total reward', totalReward)
    print()
    env.reset()
    env.close()
