#!/bin/bash
#SBATCH --account=def-mbowling
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=0-2:59
#SBATCH --array=0


# SOCKS5 Proxy
if [ "$SLURM_TMPDIR" != "" ]; then
    echo "Setting up SOCKS5 proxy..."
    ssh -q -N -T -f -D 8888 `echo $SSH_CONNECTION | cut -d " " -f 3`
    export ALL_PROXY=socks5h://localhost:8888
fi

echo "Copying virtualenv..."
cp ~/projects/def-mbowling/gwynetha/classicenv.tar.gz $SLURM_TMPDIR/
cd $SLURM_TMPDIR
tar -xzf classicenv.tar.gz
ls -l

# echo "Copying code"
# cp ~/projects/def-mbowling/gwynetha/rcrl/dqn.py $SLURM_TMPDIR/
# cd $SLURM_TMPDIR
# ls -l

echo "Cloning repo..."
git config --global http.proxy 'socks5://127.0.0.1:8888'
git clone --quiet https://github.com/swannercjj/rcrl.git $SLURM_TMPDIR/project

echo "Exporting env variables"
export PYTHONPATH=$SLURM_TMPDIR/project/
export python_venv=$SLURM_TMPDIR/virtualenvs/pyenv/bin/python3.11
echo "Running experiment..."

cd $SLURM_TMPDIR/project #put project back in for cloning repo

#declare -a learning_rates=(1e-2 5e-3 1e-3 5e-4 1e-4 5e-5 1e-5 5e-6 1e-6 5e-7)
#learning_rate=${learning_rates[$SLURM_ARRAY_TASK_ID]}
#learning_rate=0.0001

# Works for exp_fracs and tau
#declare -a exp_fracs=(1.0 0.9 0.8 0.7 0.6 0.5 0.4 0.3 0.2 0.1)
#exp_frac=${exp_fracs[$SLURM_ARRAY_TASK_ID]} 
#declare -a taus=(1)
#tau=${taus[$SLURM_ARRAY_TASK_ID]} 

#declare -a train_freqs=(1 2 4 8 16)
#train_freq=${train_freqs[$SLURM_ARRAY_TASK_ID]}
declare -a train_freqs=(1)
train_freq=${train_freqs[$SLURM_ARRAY_TASK_ID]}


#declare -a tot_steps=(250000 500000 750000 1000000 1250000)
#tot_step=${tot_steps[$SLURM_ARRAY_TASK_ID]}
#--total_timesteps $tot_step done
 
#declare -a buffer_sizes=(500 5000 50000 500000 5000000)
#buffer_size=${buffer_sizes[$SLURM_ARRAY_TASK_ID]}
#--buffer_size $buffer_size done
#declare -a buffer_sizes=(50)
#buffer_size=${buffer_sizes[$SLURM_ARRAY_TASK_ID]}

#declare -a gammas=(.99 0.9 0.8 0.7 0.6 0.5 0.4 0.3 0.2 0.1)
#gamma=${gammas[$SLURM_ARRAY_TASK_ID]}
#--gamma $gamma done
#declare -a gammas=(0.6)
#gamma=${gammas[$SLURM_ARRAY_TASK_ID]}


#declare -a target_net_freqs=(5 50 500 5000 50000)
#target_net_freq=${target_net_freqs[$SLURM_ARRAY_TASK_ID]}
#--target_network_frequency $target_net_freq done
#declare -a target_net_freqs=(5000)
#target_net_freq=${target_net_freqs[$SLURM_ARRAY_TASK_ID]}

#declare -a batch_sizes=(16 32 64 128 256)
#batch_size=${batch_sizes[$SLURM_ARRAY_TASK_ID]}
#--batch_size $batch_size
#declare -a batch_sizes=(32)
#batch_size=${batch_sizes[$SLURM_ARRAY_TASK_ID]}

#declare -a learn_starts=(10 100 1000 10000 100000)
#learning_start=${learn_starts[$SLURM_ARRAY_TASK_ID]}
#--learning_starts $learning_start
#declare -a learn_starts=(100000)
#learning_start=${learn_starts[$SLURM_ARRAY_TASK_ID]}

#declare -a ids=('Acrobot-v1' 'CartPole-v1')
#declare -a ids=('MountainCar-v0' 'LunarLander-v2')
declare -a seeds=(3 4 5)     #({2..5})
declare -a ids=('LunarLander-v2')
for env_id in "${ids[@]}"; do # reminder to change to the specific hyperparam you need
	for seed in "${seeds[@]}"; do
		$python_venv dqn.py --wandb_project_name "HyperParamSearchTrainFreq" --train_frequency $train_freq --seed $seed --no-cuda --track --env-id $env_id
	done
done

# Don't need this for wandb
#cp -r runs ~/projects/def-mbowling/gwynetha/rcrl/control_runs
