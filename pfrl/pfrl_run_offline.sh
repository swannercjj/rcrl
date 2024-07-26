#!/bin/bash
#SBATCH --account=def-mbowling
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-node=1
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

WANDB_MODE=offline PYTHONPATH=$SLURM_TMPDIR/project/:$PYTHONPATH $python_venv project/pfrl/train_dqn.py \
    --env "ALE/Pong-v5" \
    --seed $SLURM_ARRAY_TASK_ID \
    --track \
    --wandb_project_name 'PFRL_offline_0m' \
    --sanity_mod 1_000_000 \
    --steps 10_000_000

wandb sync --sync-all

results_name="results_0m_$run_timestamp.tar.gz"
tar -czf $results_name results
mkdir -p '/home/gwynetha/scratch/rcrl/pfrl/results'
cp -r $results_name '/home/gwynetha/scratch/rcrl/pfrl/results'

# Place wandb directory
wandb_dir="$(pwd)/wandb"

# Check if wandb directory exists
if [ -d "$wandb_dir" ]; then
    # Navigate to the latest run directory (assuming it's the most recent)
    latest_run_dir=$(ls -td "$wandb_dir/offline-run-"* 2>/dev/null | head -n 1)
    
    if [ -n "$latest_run_dir" ]; then
        # Extract the timestamp part (YYMMDD_HHMMSS) from the directory name
        run_id=$(basename "$latest_run_dir")
        run_timestamp=${run_id#offline-run-}  # Removes 'offline-run-' prefix
        run_timestamp=${run_timestamp%%-*}    # Keeps only YYMMDD_HHMMSS part
        
        echo "Run Timestamp: $run_timestamp"

        wandb_name="wandb_0m_$run_timestamp.tar.gz" 
        tar -czf $wandb_name wandb
        mkdir -p '/home/gwynetha/scratch/rcrl/pfrl/wandb'
        cp -r $wandb_name '/home/gwynetha/scratch/rcrl/pfrl/wandb'

    else
        echo "No run directories found in $wandb_dir"
    fi
else
    echo "WandB directory ($wandb_dir) not found."
fi
