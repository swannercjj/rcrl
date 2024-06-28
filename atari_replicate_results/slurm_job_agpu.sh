#!/bin/bash  
#SBATCH --gpus-per-node=2 
#SBATCH --account=def-mbowling
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=2:59:00
#SBATCH --array=1-50

if [ "$SLURM_TMPDIR" != "" ]; then
    echo "Setting up SOCKS5 proxy..."
    ssh -q -N -T -f -D 8888 `echo $SSH_CONNECTION | cut -d " " -f 3`
    export ALL_PROXY=socks5h://localhost:8888
fi

module load python/3.11 StdEnv/2023 gcc opencv/4.8.1 swig 

echo "Copying virtualenv..."
cp ~/projects/def-mbowling/gwynetha/atarigpuenv.tar.gz $SLURM_TMPDIR/
cd $SLURM_TMPDIR
tar -xzf atarigpuenv.tar.gz
ls -l

echo "Cloning repo..."
git config --global http.proxy 'socks5://127.0.0.1:8888'
git clone --quiet https://github.com/swannercjj/rcrl.git $SLURM_TMPDIR/project

export python_venv=$SLURM_TMPDIR/virtualenvs/pyenv/bin/python3.11

PYTHONPATH=$SLURM_TMPDIR/project/:$PYTHONPATH $python_venv project/atari_replicate_results/dqn_atari.py \
    --wandb_project_name 'Atari_Run_Replicate' \
    --seed $SLURM_ARRAY_TASK_ID \
    --total_timesteps 10000000 \
    --track \
    --learning_rate 0.00025 \
    --gamma 0.99 \
    --start_e 1.0 \
    --end_e 0.01 \
    --exploration_fraction 0.10 \
    --batch_size 32 \
    --buffer_size 1000000 \
    --train_frequency 4 \
    --env_id "BreakoutNoFrameskip-v4"
