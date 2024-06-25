#!/bin/bash
#SBATCH --account=def-mbowling
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=0-2:59


if [ "$SLURM_TMPDIR" != "" ]; then
    echo "Setting up SOCKS5 proxy..."
    ssh -q -N -T -f -D 8888 `echo $SSH_CONNECTION | cut -d " " -f 3`
    export ALL_PROXY=socks5h://localhost:8888
fi

module load python/3.11 StdEnv/2023 gcc opencv/4.8.1 swig
cd $SLURM_TMPDIR
virtualenv pyenv
source pyenv/bin/activate

echo "Installing Packages" 
pip install 'requests[socks]' --no-index
echo "has socks..." 
pip install --no-cache-dir autorom gymnasium "gymnasium[classic-control,box2d,atari,other]" "numpy<2" "stable_baselines3==2.0.0a1" tqdm tyro torch tensorboard wandb --index-url https://pypi.org/simple --extra-index-url https://download.pytorch.org/whl/cpu && \
AutoROM -y 
echo "finished installing packages" 
pip list

echo "Cloning repo..."
git config --global http.proxy 'socks5://127.0.0.1:8888'
git clone --quiet https://github.com/swannercjj/rcrl.git $SLURM_TMPDIR/project

PYTHONPATH=$SLURM_TMPDIR/project/:$PYTHONPATH python project/atari_exp/dqn_atari.py \
    --wandb_project_name \"Atari_Run\" \
    --no-cuda \
    --track

echo "done"