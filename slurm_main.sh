#!/bin/bash
#SBATCH --account=def-mbowling
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=0-2:59

# this bash file creates a command that calls another script 'slurm_job.sh'. Hold values of seeds
# other script unzips folder and runs the experiment
# dictionary of {'param name':['project_name', 'var_name', (array of values)]}
<<com
seed from job array
#SBATCH --array=6-20
command=  $python_venv dqn.py --wandb_project_name "HyperParamSearch"+"project_name" --var_name $array_val --seed $seed --no-cuda --track --env-id $env_id
com
cd /home/gwynetha/projects/def-mbowling/gwynetha/rcrl

declare -A params=(
    [learning_rate]='LearningRate 1e-2 5e-3 1e-3 5e-4 1e-4 5e-5 1e-5 5e-6 1e-6 5e-7'
    [buffer_size]='BufferSize 500 5000 50000 500000 5000000'
    [gamma]='Gamma .99 0.9 0.8 0.7 0.6 0.5 0.4 0.3 0.2 0.1'
    [tau]='Tau 1.0 0.9 0.8 0.7 0.6 0.5 0.4 0.3 0.2 0.1'
    [target_network_frequency]='TargetNetFreq 5 50 500 5000 50000'
    [batch_size]='BatchSize 16 32 64 128 256'
    [exploration_fraction]='ExpFrac 1.0 0.9 0.8 0.7 0.6 0.5 0.4 0.3 0.2 0.1'
    [learning_starts]='LearningStart 10 100 1000 10000 100000'
    [train_frequency]='TrainFreq 1 2 4 8 16'
)

declare -a ids=('Acrobot-v1' 'CartPole-v1' 'MountainCar-v0' 'LunarLander-v2')

chmod +x slurm_job.sh 

for env_id in "${ids[@]}"; do 
    for param in "${!params[@]}"; do
        # Split the value of params[$param] into an array
        read -r param_name values <<< "${params[$param]}"

        echo "Parameter: $param_name"

        for val in $values; do
            command="dqn.py --wandb_project_name \"HyperParamSearch${param_name}\" --$param $val --no-cuda --track --env-id $env_id"
            echo "$command"
            sbatch slurm_job.sh "$command" 
        done
    done
done



