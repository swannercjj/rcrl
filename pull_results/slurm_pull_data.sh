#!/bin/bash
#SBATCH --account=def-mbowling
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=0-2:59

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
# for when branches are merged
# git clone --quiet https://github.com/swannercjj/rcrl.git $SLURM_TMPDIR/
git clone --quiet https://github.com/swannercjj/rcrl.git --branch comparison-check --single-branch $SLURM_TMPDIR/project

echo "Exporting env variables"
export PYTHONPATH=$SLURM_TMPDIR/project/
export python_venv=$SLURM_TMPDIR/virtualenvs/pyenv/bin/python3.11

echo "Running experiment..."
cd $SLURM_TMPDIR/project/pull_results
$python_venv pull_data.py --project name HyperParamSearchLr --hyperparam learning_rate
tar -czf data.tar.gz data
cp data.tar.gz ~/projects/def-mbowling/jiajing8/rcrl/
