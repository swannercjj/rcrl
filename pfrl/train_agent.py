import logging
import os
import wandb
import time
import numpy as np
from PIL import Image 

from tests.pytests import check_first_frame
from pfrl.experiments.evaluator import save_agent
from evaluator import Evaluator
from pfrl.utils.ask_yes_no import ask_yes_no

import tracemalloc


def save_agent_replay_buffer(agent, t, outdir, suffix="", logger=None):
    logger = logger or logging.getLogger(__name__)
    filename = os.path.join(outdir, "{}{}.replay.pkl".format(t, suffix))
    agent.replay_buffer.save(filename)
    logger.info("Saved the current replay buffer to %s", filename)


def ask_and_save_agent_replay_buffer(agent, t, outdir, suffix=""):
    if hasattr(agent, "replay_buffer") and ask_yes_no(
        "Replay buffer has {} transitions. Do you save them to a file?".format(
            len(agent.replay_buffer)
        )
    ):  # NOQA
        save_agent_replay_buffer(agent, t, outdir, suffix=suffix)

def image_obs(obs, im_obs, name=str): # for logging images on wandb
    '''obs is an array of the observation'''
    im = Image.fromarray(obs)
    im.save(str(name)+".jpeg")
    f = open(str(name)+".txt", "a")
    f.write(str(obs))
    f.close()
    
    # create wandb image, put in list of images
    im_wandb = wandb.Image(im, caption=name)
    im_obs.append(im_wandb)

def train_agent(
    agent,
    env,
    steps,
    outdir,
    checkpoint_freq=None,
    max_episode_len=None,
    step_offset=0,
    evaluator=None,
    successful_score=None,
    step_hooks=(),
    eval_during_episode=False,
    use_tensorboard=False,
    logger=None,
    sanity_mod=None, ### for image observations checks
    action_repeat_n=1
):
    begin = int(time.time())
    logger = logger or logging.getLogger(__name__)

    episode_r = 0
    episode_idx = 0

    # o_0, r_0
    obs , info = env.reset()
    im_obs = []

    t = step_offset
    if hasattr(agent, "t"):
        agent.t = step_offset

    eval_stats_history = []  # List of evaluation episode stats dict
    episode_len = 0
    #repeat = True ######
    #rep_count = 1
    
    print("CONSTANT REPEATS!")
    try:
        action = 0
        while t < steps:
            if use_tensorboard: # logging memory usage
                evaluator.tb_writer.add_scalar("memory/memory_usage_gb", float(tracemalloc.get_traced_memory()[0]) * 1e-9)
                
            if t == 0: # test of if first frame is reset properly
                check_first_frame(env,obs)

            if sanity_mod !=None and t%sanity_mod == 0:
                name = str(t)+"_"+"before_obs_"+str(action)+"_"+str(begin)
                obs_numpy = np.asarray(obs)
                before = obs_numpy[0]
                image_obs(before, im_obs, name)
            
            # a_t
            action = agent.act(obs)
            unclipped_r = 0
            
            if agent.mode == 1:
                # constant repeat actions
                for rep in range(action_repeat_n):
                    # o_{t+1}, r_{t+1}
                    obs, r, terminated, truncated, info = env.step(action)
                    unclipped_r += (agent.gamma ** rep) * r # accumulated reward from repeated action
                    t += 1
                    episode_len += 1
                    if terminated or info.get("needs reset", False) or truncated:
                        break
                        
            if agent.mode == 2 and len(agent.action_repeats) > 1:
                # learn to repeat
                repeat = agent.action_repeats[action % len(agent.action_repeats)]
                action = action // len(agent.action_repeats)
                for _ in range(repeat):
                    obs, r, terminated, truncated, info = env.step(action)
                    t += 1
                    unclipped_r += r  # unclipped, currently not discounted
                    episode_len += 1
                    if terminated or info.get("needs_reset", False) or truncated:
                        break
                if use_tensorboard:
                    evaluator.tb_writer.add_scalar("actions/num_repeats", repeat, t)
            else:
                # default
                obs, r, terminated, truncated, info = env.step(action)
                t += 1
                episode_len += 1
                unclipped_r += r  # unclipped, currently not discounted

            # checking individual frames
            if sanity_mod !=None and t%sanity_mod == 0:
                name = str(t)+"+1_"+"after_obs_"+str(action)+"_"+str(begin)
                obs_numpy = np.asarray(obs)
                after = obs_numpy[0]
                image_obs(after, im_obs, name)

            episode_r += unclipped_r
            reset = episode_len == max_episode_len or info.get("needs_reset", False) or truncated
            clipped_r = np.sign(rep_r) ##### Clipping repeated rewards, choice point
            agent.observe(obs, clipped_r, terminated, reset)


            for hook in step_hooks:
                hook(env, agent, t)

            episode_end = terminated or reset or t == steps

            if episode_end:
                logger.info(
                    "outdir:%s step:%s episode:%s R:%s",
                    outdir,
                    t,
                    episode_idx,
                    episode_r,
                )
                if use_tensorboard:
                    evaluator.tb_writer.add_scalar("charts/episodic_return", episode_r, t)
                stats = agent.get_statistics()
                logger.info("statistics:%s", stats)
                episode_idx += 1

            if evaluator is not None and (episode_end or eval_during_episode):
                eval_score = evaluator.evaluate_if_necessary(t=t, episodes=episode_idx)
                if eval_score is not None:
                    eval_stats = dict(agent.get_statistics())
                    eval_stats["eval_score"] = eval_score
                    eval_stats_history.append(eval_stats)
                if (
                    successful_score is not None
                    and evaluator.max_score >= successful_score
                ):
                    break

            if episode_end:
                if t == steps:
                    if sanity_mod !=None:
                        wandb.log({"Sanity Check": im_obs})
                    break
                # Start a new episode
                episode_r = 0
                episode_len = 0
                obs, info = env.reset()
            if checkpoint_freq and t % checkpoint_freq == 0:
                save_agent(agent, t, outdir, logger, suffix="_checkpoint")

    except (Exception, KeyboardInterrupt):
        # Save the current model before being killed
        save_agent(agent, t, outdir, logger, suffix="_except")
        raise

    # Save the final model
    save_agent(agent, t, outdir, logger, suffix="_finish")

    return eval_stats_history


def train_agent_with_evaluation(
    agent,
    env,
    steps,
    eval_n_steps,
    eval_n_episodes,
    eval_interval,
    outdir,
    checkpoint_freq=None,
    train_max_episode_len=None,
    step_offset=0,
    eval_max_episode_len=None,
    eval_env=None,
    successful_score=None,
    step_hooks=(),
    evaluation_hooks=(),
    save_best_so_far_agent=True,
    use_tensorboard=False,
    eval_during_episode=False,
    logger=None,
    sanity_mod=None, ### for image observations checks
    action_repeat_n = 1,

):
    """Train an agent while periodically evaluating it.

    Args:
        agent: A pfrl.agent.Agent
        env: Environment train the agent against.
        steps (int): Total number of timesteps for training.
        eval_n_steps (int): Number of timesteps at each evaluation phase.
        eval_n_episodes (int): Number of episodes at each evaluation phase.
        eval_interval (int): Interval of evaluation.
        outdir (str): Path to the directory to output data.
        checkpoint_freq (int): frequency at which agents are stored.
        train_max_episode_len (int): Maximum episode length during training.
        step_offset (int): Time step from which training starts.
        eval_max_episode_len (int or None): Maximum episode length of
            evaluation runs. If None, train_max_episode_len is used instead.
        eval_env: Environment used for evaluation.
        successful_score (float): Finish training if the mean score is greater
            than or equal to this value if not None
        step_hooks (Sequence): Sequence of callable objects that accepts
            (env, agent, step) as arguments. They are called every step.
            See pfrl.experiments.hooks.
        evaluation_hooks (Sequence): Sequence of
            pfrl.experiments.evaluation_hooks.EvaluationHook objects. They are
            called after each evaluation.
        save_best_so_far_agent (bool): If set to True, after each evaluation
            phase, if the score (= mean return of evaluation episodes) exceeds
            the best-so-far score, the current agent is saved.
        use_tensorboard (bool): Additionally log eval stats to tensorboard
        eval_during_episode (bool): Allow running evaluation during training episodes.
            This should be enabled only when `env` and `eval_env` are independent.
        logger (logging.Logger): Logger used in this function.
    Returns:
        agent: Trained agent.
        eval_stats_history: List of evaluation episode stats dict.
    """

    logger = logger or logging.getLogger(__name__)

    for hook in evaluation_hooks:
        if not hook.support_train_agent:
            raise ValueError(
                "{} does not support train_agent_with_evaluation().".format(hook)
            )

    os.makedirs(outdir, exist_ok=True)

    if eval_env is None:
        assert not eval_during_episode, (
            "To run evaluation during training episodes, you need to specify `eval_env`"
            " that is independent from `env`."
        )
        eval_env = env

    if eval_max_episode_len is None:
        eval_max_episode_len = train_max_episode_len

    evaluator = Evaluator(
        agent=agent,
        n_steps=eval_n_steps,
        n_episodes=eval_n_episodes,
        eval_interval=eval_interval,
        outdir=outdir,
        max_episode_len=eval_max_episode_len,
        env=eval_env,
        step_offset=step_offset,
        evaluation_hooks=evaluation_hooks,
        save_best_so_far_agent=save_best_so_far_agent,
        use_tensorboard=use_tensorboard,
        logger=logger,
    )

    eval_stats_history = train_agent(
        agent,
        env,
        steps,
        outdir,
        checkpoint_freq=checkpoint_freq,
        max_episode_len=train_max_episode_len,
        step_offset=step_offset,
        evaluator=evaluator,
        successful_score=successful_score,
        step_hooks=step_hooks,
        eval_during_episode=eval_during_episode,
        use_tensorboard=use_tensorboard,
        logger=logger,
        sanity_mod=sanity_mod,
        action_repeat_n = action_repeat_n
    )

    return agent, eval_stats_history
