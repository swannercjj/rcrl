import argparse
import json
import os

import numpy as np
import torch.nn as nn

import time
import pfrl
from pfrl import agents, experiments, explorers
from pfrl import nn as pnn
from pfrl import replay_buffers, utils
from pfrl.initializers import init_chainer_default
from pfrl.q_functions import DiscreteActionValueHead
import atari_wrappers
import train_agent
import evaluator
import tracemalloc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--exp_name",
        type=str,
        default=os.path.basename(__file__)[: -len(".py")],
        help="Experiment name."
    )
    parser.add_argument(
        "--track",
        action="store_true",
        default=False,
        help="Log results to wandb."
    )
    parser.add_argument(
        "--wandb_project_name",
        type=str,
        default="pfrl_test",
        help="Wandb project's name."
    )
    parser.add_argument(
        "--wandb_entity",
        type=str,
        default="rcrl",
        help="Entity (team) of wandb's project."
    )
    parser.add_argument("--wandb_mode", type=str, default="online", help="Mode for wandb logging.")

    parser.add_argument(
        "--env",
        type=str,
        default="ALE/SpaceInvaders-v5",
        help="OpenAI Atari domain to perform algorithm on.",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default="results",
        help=(
            "Directory path to save output files."
            " If it does not exist, it will be created."
        ),
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed [0, 2 ** 31)")
    parser.add_argument(
        "--gpu", type=int, default=0, help="GPU to use, set to -1 if no GPU."
    )
    parser.add_argument("--demo", action="store_true", default=False)
    parser.add_argument("--load-pretrained", action="store_true", default=False)
    parser.add_argument(
        "--pretrained-type", type=str, default="best", choices=["best", "final"]
    )
    parser.add_argument("--load", type=str, default=None)
    parser.add_argument(
        "--log-level",
        type=int,
        default=20,
        help="Logging level. 10:DEBUG, 20:INFO etc.",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        default=False,
        help="Render env states in a GUI window.",
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        default=False,
        help=(
            "Monitor env. Videos and additional information are saved as output files."
        ),
    )
    parser.add_argument( 
        "--steps",
        type=int,
        default=5 * 10**7,
        help="Total number of timesteps to train the agent.",
    ) ## steps vs decsions??

    parser.add_argument("--eval-n-steps", type=int, default=125000)
    parser.add_argument("--eval-interval", type=int, default=250000)
    parser.add_argument("--n-best-episodes", type=int, default=30)

    # optimizer
    parser.add_argument("--opt-lr", type=float, default=2.5e-4)
    parser.add_argument("--opt-alpha", type=float, default=0.95)
    parser.add_argument("--opt-momentum", type=float, default=0.0)
    parser.add_argument("--opt-eps", type=float, default=1e-2)

    # replay buffer
    parser.add_argument("--start-epsilon", type=float, default=1.0)
    parser.add_argument("--end-epsilon", type=float, default=0.01)
    parser.add_argument("--decay-steps", type=float, default=10**6)

    # agent
    parser.add_argument("--agt-target-update-interval", type=int, default=10**4)
    parser.add_argument("--agt-update-interval", type=int, default=4)
    parser.add_argument(
        "--replay-start-size",
        type=int,
        default=5 * 10**4,
        help="Minimum replay buffer size before " + "performing gradient updates.",
    )
    parser.add_argument("--frame-skip", type=int, default=5)
    parser.add_argument("--action-repeat-n", type=int, default=1)

    # added for logging
    parser.add_argument("--sanity-mod", type=int, default=None)

    # action repeats
    parser.add_argument("--mode",
                        type=int,
                        choices=[0, 1],
                        default=0,
                        help="Mode for the agent. 0: default (normal dqn), 1: learn to repeat actions.")
    parser.add_argument("--repeat-options", nargs="+", type=int, default="1")

    # unit of time
    parser.add_argument("--time-mode",
                        type=int,
                        choices=[0,1],
                        default=0,
                        help="Mode for the time unit. 0: default (global time step, each action = t.) 1: decision (each new choice of action = t)"
                        )
    args = parser.parse_args()

    import logging

    logging.basicConfig(level=args.log_level)

    # wandb logging
    if args.track:
        import wandb
        run_name = f"{args.env}__{args.exp_name}__{args.seed}__{int(time.time())}"

        wandb.init(
            project=args.wandb_project_name,
            entity=args.wandb_entity,
            sync_tensorboard=True,
            config=vars(args),
            name=run_name,
            monitor_gym=True,
            save_code=True,
            mode=args.wandb_mode
        )

    # Set a random seed used in PFRL.
    utils.set_random_seed(args.seed)

    # Set different random seeds for train and test envs.
    train_seed = args.seed
    test_seed = 2**31 - 1 - args.seed

    args.outdir = experiments.prepare_output_dir(args, args.outdir)
    print("Output files are saved in {}".format(args.outdir))
    run_name = f"{args.env}__{args.seed}__{int(time.time())}"

    def make_env(test):
        # Use different random seeds for train and test envs
        env_seed = test_seed if test else train_seed
        env = atari_wrappers.wrap_deepmind(
            atari_wrappers.make_atari_sticky(args.env, max_frames=None, frame_skip=args.frame_skip), # originally used to be make_atari
            episode_life=not test,
            clip_rewards=False,
        )
        env.seed(int(env_seed))
        if test:
            # Randomize actions like epsilon-greedy in evaluation as well
            env = pfrl.wrappers.RandomizeAction(env, 0.01) # marlos paper, default 0.05 
        if args.monitor:
            env = pfrl.wrappers.Monitor(
                env, args.outdir, mode="evaluation" if test else "training"
            )
        if args.render:
            env = pfrl.wrappers.Render(env)
        return env

    env = make_env(test=False)
    eval_env = make_env(test=True)

    n_actions = env.action_space.n * len(args.repeat_options) if args.mode == 1 else env.action_space.n
    q_func = nn.Sequential(     
        pnn.LargeAtariCNN(),
        init_chainer_default(nn.Linear(512, n_actions)),
        DiscreteActionValueHead(),
    )

    # Use the same hyperparameters as the Nature paper

    opt = pfrl.optimizers.RMSpropEpsInsideSqrt(
        q_func.parameters(),
        lr=args.opt_lr,  # step size
        alpha=args.opt_alpha, # smoothing constant
        momentum=args.opt_momentum,  # default 0.0
        eps=args.opt_eps,   # min squared gradient
        centered=True,
    )

    rbuf = replay_buffers.ReplayBuffer(10**6)

    explorer = explorers.LinearDecayEpsilonGreedy(
        start_epsilon=args.start_epsilon,
        end_epsilon=args.end_epsilon,   # default 0.1
        decay_steps=args.decay_steps,
        random_action_func=lambda: np.random.randint(n_actions),
    )

    def phi(x):
        # Feature extractor
        return np.asarray(x, dtype=np.float32) / 255

    Agent = agents.DQN
    agent = Agent(
        q_func,
        opt,
        rbuf,
        gpu=args.gpu,
        gamma=0.99,
        explorer=explorer,
        replay_start_size=args.replay_start_size,
        target_update_interval=args.agt_target_update_interval,
        clip_delta=True,
        update_interval=args.agt_update_interval,
        batch_accumulator="sum",
        phi=phi,
    )
    agent.time_mode = args.time_mode
    agent.mode = args.mode
    agent.repeat_n = args.action_repeat_n
    # agent add action repeats
    agent.action_repeats = args.repeat_options # list

    if args.load or args.load_pretrained:
        # either load or load_pretrained must be false
        assert not args.load or not args.load_pretrained
        if args.load:
            agent.load(args.load)
        else:
            agent.load(
                utils.download_model("DQN", args.env, model_type=args.pretrained_type)[
                    0
                ]
            )

    tracemalloc.start()

    if args.demo:
        eval_stats = experiments.eval_performance(
            env=eval_env, agent=agent, n_steps=args.eval_n_steps, n_episodes=None
        )
        print(
            "n_episodes: {} mean: {} median: {} stdev {}".format(
                eval_stats["episodes"],
                eval_stats["mean"],
                eval_stats["median"],
                eval_stats["stdev"],
            )
        )
    else:
        train_agent.train_agent_with_evaluation(
            agent=agent,
            env=env,
            steps=args.steps,
            eval_n_steps=args.eval_n_steps,
            eval_n_episodes=None,
            eval_interval=args.eval_interval,
            outdir=args.outdir,
            save_best_so_far_agent=True,
            eval_env=eval_env,
            use_tensorboard=True,
            sanity_mod=args.sanity_mod, # for image observations checks
        )
        tracemalloc.stop()

        dir_of_best_network = os.path.join(args.outdir, "best")
        agent.load(dir_of_best_network)

        # run 30 evaluation episodes, each capped at 5 mins of play
        stats = evaluator.eval_performance(
            env=eval_env,
            agent=agent,
            n_steps=None,
            n_episodes=args.n_best_episodes,
            max_episode_len=27000, #27_000,30 MINS IN EMULATOR # default 4500
            logger=None,
        )
        with open(os.path.join(args.outdir, "bestscores.json"), "w") as f:
            json.dump(stats, f)
        print("The results of the best scoring network:")
        for stat in stats:
            print(str(stat) + ":" + str(stats[stat]))


if __name__ == "__main__":
    main()

