import os
import numpy as np

def discount(reward, gamma):
    rep_r = 0
    for rep in range(len(reward)):
        rep_r += (gamma ** rep) * reward[rep] # accumulated reward from repeated action
    return rep_r

def first_frame(env):
    obs , info = env.reset()
    return np.asarray(obs)
    
    
def test_discount():
    reward = [0,1,2,3,4,5]
    gamma = 0.9
    result = reward[0]*gamma**0 + reward[1]*gamma**1 + reward[2]*gamma**2 + reward[3]*gamma**3 + reward[4]*gamma**4 + reward[5]*gamma**5  
    assert discount(reward, gamma) == result

def check_first_frame(env,obs):
    #pathname= os.path.join(os.getcwd(),'project', 'pfrl', 'tests','frame_check', 'first_frames.npz')
    pathname= os.path.join(os.getcwd(),'tests','frame_check', 'first_frames.npz')
    saved_dict = np.load(pathname)
    saved_first_frame = saved_dict[str(env.spec.id)]
    assert (np.asarray(obs)==saved_first_frame).all(), 'The reset frame does not match the reset state'
