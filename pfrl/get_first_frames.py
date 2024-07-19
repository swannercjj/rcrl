import atari_wrappers
import os
import numpy as np
from PIL import Image

atari_games = [
    'ALE/Adventure-v5',
    'ALE/AirRaid-v5',
    'ALE/Alien-v5',
    'ALE/Amidar-v5',
    'ALE/Assault-v5',
    'ALE/Asterix-v5',
    'ALE/Asteroids-v5',
    'ALE/Atlantis-v5',
    'ALE/BankHeist-v5',
    'ALE/BattleZone-v5',
    'ALE/BeamRider-v5',
    'ALE/Berzerk-v5',
    'ALE/Bowling-v5',
    'ALE/Boxing-v5',
    'ALE/Breakout-v5',
    'ALE/Carnival-v5',
    'ALE/Centipede-v5',
    'ALE/ChopperCommand-v5',
    'ALE/CrazyClimber-v5',
    'ALE/DemonAttack-v5',
    'ALE/DoubleDunk-v5',
    'ALE/ElevatorAction-v5',
    'ALE/Enduro-v5',
    'ALE/FishingDerby-v5',
    'ALE/Freeway-v5',
    'ALE/Frostbite-v5',
    'ALE/Gopher-v5',
    'ALE/Gravitar-v5',
    'ALE/Hero-v5',
    'ALE/IceHockey-v5',
    'ALE/Jamesbond-v5',
    'ALE/JourneyEscape-v5',
    'ALE/Kangaroo-v5',
    'ALE/Krull-v5',
    'ALE/KungFuMaster-v5',
    'ALE/MontezumaRevenge-v5',
    'ALE/MsPacman-v5',
    'ALE/NameThisGame-v5',
    'ALE/Phoenix-v5',
    'ALE/Pitfall-v5',
    'ALE/Pong-v5',
    'ALE/Pooyan-v5',
    'ALE/PrivateEye-v5',
    'ALE/Qbert-v5',
    'ALE/Riverraid-v5',
    'ALE/RoadRunner-v5',
    'ALE/Robotank-v5',
    'ALE/Seaquest-v5',
    'ALE/Skiing-v5',
    'ALE/Solaris-v5',
    'ALE/SpaceInvaders-v5',
    'ALE/StarGunner-v5',
    'ALE/Tennis-v5',
    'ALE/TimePilot-v5',
    'ALE/Tutankham-v5',
    'ALE/UpNDown-v5',
    'ALE/Venture-v5',
    'ALE/VideoPinball-v5',
    'ALE/WizardOfWor-v5',
    'ALE/YarsRevenge-v5',
    'ALE/Zaxxon-v5'
]




def make_env(test=False, env_name=str):
        # Use different random seeds for train and test envs
        env = atari_wrappers.wrap_deepmind(
            atari_wrappers.make_atari_sticky(env_name, max_frames=None),
            episode_life=not test,
            clip_rewards=not test,
                )
        return env

def image_obs(obs, env_name): # for logging images on wandb
    '''obs is an array of the observation'''
    print('Making image for',env_name)
    im = Image.fromarray(obs)
    os.makedirs(os.path.join('frame_check', 'frame_images'), exist_ok=True)
    name = os.path.join('frame_check', 'frame_images', f'{env_name[4:]}_first_frame')
    im.save(str(name)+".jpeg")


first_frames = {}
for env_name in atari_games:
    env = make_env(env_name=env_name)
    obs , info = env.reset()
    obs_numpy = np.asarray(obs)
    first_frames[env_name] = obs_numpy
    image_obs(obs = obs_numpy[0], env_name=env_name)

os.makedirs('frame_check', exist_ok=True)
pathname= os.path.join('frame_check', 'first_frames.npz')
np.savez(pathname, **first_frames)