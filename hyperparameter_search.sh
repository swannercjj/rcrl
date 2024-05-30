#!/bin/bash
# the different params
# seed  total_timesteps	 learning_rate	num_envs	buffer_size	gamma	tau	target_network_frequency	batch_size	start_e	end_e		

# add on hyperparameters
declare -a seeds=(1 2 3)
declare -a learning_rates=(2.5e-4) 
declare -a batch_sizes=(128)

# Grid Search: add on a for loop for every new hyperparameter
for seed in "${seeds[@]}"; do
    for learning_rate in "${learning_rates[@]}"; do
        for batch_size in "${batch_sizes[@]}"; do
            # Change the directory to where your code is
            command="python3 '/Users/gwendls/Desktop/Research 2024/rcrl/dqn.py' --seed $seed --learning_rate $learning_rate --batch_size $batch_size"
            echo "Running command: $command"
            eval $command
        done
    done
done

