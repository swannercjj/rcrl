#!/bin/bash
#SBATCH --account=def-mbowling
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=0-2:59
#SBATCH --array=0-29

# SOCKS5 Proxy
if [ "$SLURM_TMPDIR" != "" ]; then
    echo "Setting up SOCKS5 proxy..."
    ssh -q -N -T -f -D 8888 `echo $SSH_CONNECTION | cut -d " " -f 3`
    export ALL_PROXY=socks5h://localhost:8888
fi

echo "Copying virtualenv..."
cp ~/projects/def-mbowling/jiajing8/pyenv.tar.gz $SLURM_TMPDIR/
cd $SLURM_TMPDIR
tar -xzf pyenv.tar.gz
ls -l

echo "Cloning repo..."
git config --global http.proxy 'socks5://127.0.0.1:8888'
git clone --quiet https://github.com/swannercjj/rcrl.git $SLURM_TMPDIR/project

echo "Exporting env variables"
export PYTHONPATH=$SLURM_TMPDIR/project/
export python_venv=$SLURM_TMPDIR/virtualenvs/pyenv/bin/python3.11
echo "Running experiment..."

cd $SLURM_TMPDIR/project/pull_results # put project back in for cloning repo
git checkout comparison-check
$python_venv pull_data.py --entity_name openrlbenchmark
# $python_venv dqn.py --seed $SLURM_ARRAY_TASK_ID --track --wandb_project_name 'Acrobot_Trials2.0' --env_id 'Acrobot-v1'