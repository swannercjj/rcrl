#!/bin/bash
#SBATCH --account=def-mbowling
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G       
#SBATCH --time=0-2:59

# SOCKS5 Proxy
if [ "$SLURM_TMPDIR" != "" ]; then
    echo "Setting up SOCKS5 proxy..."
    ssh -q -N -T -f -D 8888 `echo $SSH_CONNECTION | cut -d " " -f 3`
    export ALL_PROXY=socks5h://localhost:8888
fi

# Setup Modules
module load python
echo "load python"

# Setup Python Environment
cd $SLURM_TMPDIR
virtualenv pyenv
. pyenv/bin/activate
pip install 'requests[socks]' --no-index
pip install -r /home/gwynetha/projects/def-mbowling/gwynetha/rcrl/control_req.txt --no-index

seeds=({0..29})
env_id="CartPole-v1"


for seed in "${seeds[@]}"; do
# Change the directory to where your code is
    command="python3 '/home/gwynetha/projects/def-mbowling/gwynetha/rcrl/dqn.py' --env_id $env_id --seed $seed"
    echo "Running command: $command"
    eval $command
done

# copy the folder from tmpdir to local folder. (dqn code makes folder runs, then in the runs folder has env folder)
# not sure if I need it for when wandb is toggled though
cp -r runs ~/projects/def-mbowling/gwynetha/control_runs
          
