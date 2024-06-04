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

echo "Copying virtualenv..."
cp ~/projects/def-mbowling/gwynetha/classicenv.tar.gz $SLURM_TMPDIR/
cd $SLURM_TMPDIR
tar -xzf classicenv.tar.gz
ls -l

echo "Copying code"
cp ~/projects/def-mbowling/gwynetha/rcrl/dqn.py $SLURM_TMPDIR/
cd $SLURM_TMPDIR
ls -l

echo "Exporting env variables"
export python_venv=$SLURM_TMPDIR/virtualenvs/classicenv/bin/python3.10
echo "Running experiment..."
cd $SLURM_TMPDIR
$python_venv dqn.py
cp -r runs ~/projects/def-mbowling/gwynetha/rcrl/control_runs
