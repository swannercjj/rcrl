#!/bin/bash
#SBATCH --account=def-mbowling
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=0-2:59

declare -a command="$1"
echo 'job script'
echo $command
#<<com
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

echo "Cloning repo..."
git config --global http.proxy 'socks5://127.0.0.1:8888'
git clone --quiet https://github.com/swannercjj/rcrl.git $SLURM_TMPDIR/project

echo "Exporting env variables"
export PYTHONPATH=$SLURM_TMPDIR/project/
export python_venv=$SLURM_TMPDIR/virtualenvs/pyenv/bin/python3.11
echo "Running experiment..."
#com

cd $SLURM_TMPDIR/project
echo "Running command: $python_venv $command"
eval "$python_venv $command"

