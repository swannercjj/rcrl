#!/bin/bash  
#SBATCH --gpus-per-node=1
#SBATCH --account=def-mbowling
#SBATCH --cpus-per-task=1
#SBATCH --mem=10G
#SBATCH --time=36:00:00
#SBATCH --array=1-50

if [ "$SLURM_TMPDIR" != "" ]; then
    echo "Setting up SOCKS5 proxy..."
    ssh -q -N -T -f -D 8888 `echo $SSH_CONNECTION | cut -d " " -f 3`
    export ALL_PROXY=socks5h://localhost:8888
fi

module load python/3.11 StdEnv/2023 gcc opencv/4.8.1 swig 

echo "Copying virtualenv..."
cp ~/projects/def-mbowling/jiajing8/pfrlenv.tar.gz $SLURM_TMPDIR/
cd $SLURM_TMPDIR
tar -xzf pfrlenv.tar.gz
ls -l

echo "Cloning repo..."
git config --global http.proxy 'socks5://127.0.0.1:8888'
git clone --quiet -b learn-action-repeats https://github.com/swannercjj/rcrl.git $SLURM_TMPDIR/project

export python_venv=$SLURM_TMPDIR/virtualenvs/pyenv/bin/python3.11

export WANDB_MODE=online
PYTHONPATH=$SLURM_TMPDIR/project/:$PYTHONPATH $python_venv project/pfrl/train_dqn.py \
    --env "ALE/Pong-v5" \
    --seed $SLURM_ARRAY_TASK_ID \
    --track \
    --wandb_project_name 'Pfrl_Learn_AR_Pong' \
    --sanity_mod 1_000_000 \
    --steps 10_000_000 \
    --repeat-options 1 4

cp -r results '/home/jiajing8/scratch/rcrl/pfrl/results'
