#!/bin/bash  
#SBATCH --gpus-per-node=1
#SBATCH --account=def-mbowling
#SBATCH --cpus-per-task=1
#SBATCH --mem=10G
#SBATCH --time=1-0
#SBATCH --array=1-50

if [ "$SLURM_TMPDIR" != "" ]; then
    echo "Setting up SOCKS5 proxy..."
    ssh -q -N -T -f -D 8888 `echo $SSH_CONNECTION | cut -d " " -f 3`
    export ALL_PROXY=socks5h://localhost:8888
fi

module load python/3.11 StdEnv/2023 gcc opencv/4.8.1 swig 

echo "Copying virtualenv..."
cp ~/projects/def-mbowling/gwynetha/pfrlenv.tar.gz $SLURM_TMPDIR/
cd $SLURM_TMPDIR
tar -xzf pfrlenv.tar.gz
ls -l

echo "Cloning repo..."
git config --global http.proxy 'socks5://127.0.0.1:8888'
git clone --quiet https://github.com/swannercjj/rcrl.git $SLURM_TMPDIR/project

export python_venv=$SLURM_TMPDIR/virtualenvs/pyenv/bin/python3.11

wandb online
PYTHONPATH=$SLURM_TMPDIR/project/:$PYTHONPATH $python_venv project/pfrl/train_dqn.py \
    --env "ALE/Pong-v5" \
    --seed $SLURM_ARRAY_TASK_ID \
    --track \
    --wandb_project_name 'Pfrl_Pong_Paper_0m' \
    --sanity_mod 1000000 \
    --steps 10000000

cp -r results '/home/gwynetha/projects/def-mbowling/gwynetha/rcrl/pfrl/results'
