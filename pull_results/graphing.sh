#!/bin/bash

# Pulls data from wandb and 

# Define parameters as separate arrays
learning_rate=('Lr' '1e-2' '5e-3' '1e-3' '5e-4' '1e-4' '5e-5' '1e-5' '5e-6' '1e-6' '5e-7')
buffer_size=('BufferSize' '500' '5000' '50000' '500000' '5000000')
gamma=('Gamma' '0.99' '0.9' '0.8' '0.7' '0.6' '0.5' '0.4' '0.3' '0.2' '0.1')
tau=('Tau' '1.0' '0.9' '0.8' '0.7' '0.6' '0.5' '0.4' '0.3' '0.2' '0.1')
target_network_frequency=('TargetNetFreq' '5' '50' '500' '5000' '50000')
batch_size=('BatchSize' '16' '32' '64' '128' '256')
exploration_fraction=('ExpFrac' '1.0' '0.9' '0.8' '0.7' '0.6' '0.5' '0.4' '0.3' '0.2' '0.1')
learning_starts=('LearningStart' '10' '100' '1000' '10000' '100000')
train_frequency=('TrainFreq' '1' '2' '4' '8' '16')

#Iterate over each parameter array
for param_array in learning_rate buffer_size gamma tau target_network_frequency batch_size exploration_fraction learning_starts train_frequency; do
    param_name="${!param_array[0]}"

    echo "Parameter: $param_name"

    # project_name="HyperParamSearch${param_name}"
    # command="python3 'pull_data.py' --project_name $project_name --hyperparam $param_array"
    # echo "Pulling Data: $command"
    # eval $command

    command="python3 'plot_graph.py' --hyperparam $param_array"
    echo "Making graph: $command"
    eval $command

done

