import pandas as pd
import matplotlib.pyplot as plt
import os
from dataclasses import dataclass
import tyro
import numpy as np


@dataclass
class Args:
    hyperparam: str = "learning_rate"
    "Hyperparameter to plot."


if __name__=="__main__":
    args = tyro.cli(Args)

    file_path = os.path.join(f"./data/{args.hyperparam}.csv")

    x_vals = {
    'learning_rate': [1e-2, 5e-3, 1e-3, 5e-4, 1e-4, 5e-5, 1e-5, 5e-6, 1e-6, 5e-7, 'Learning Rate'],
    'buffer_size':[500,5000, 50000, 500000, 5000000 ,'Buffer Size'],
    'gamma':[.99, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 'Gamma'],
    'tau':[1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, "Tau"],
    'target_network_frequency':[5, 50, 500, 5000, 50000, "Target Network Frequency"],
    'batch_size':[16, 32, 64, 128, 256, 'Batch Size'],
    'exploration_fraction': [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 'Exploration Fraction'],
    'learning_starts': [10, 100, 1000, 10000, 100000, 'Learning Starts'],
    'train_frequency': [1, 2, 4, 8, 16, "Train Frequency"]
    }

    if not os.path.exists(file_path):
        print(f"Data for {args.hyerparam} does not exist.")
        exit()

    # Read file
    df = pd.read_csv(file_path)

    # Group by 'env_id', hyperparameter and average 'mean_episodic_return'
    grouped_df = df.groupby(['env_id', args.hyperparam])['mean_episodic_return'].mean().reset_index()

    # Plot the data
    plt.figure(figsize=(10, 6))
    labels = x_vals[args.hyperparam][:-1]
    
    evenly_spaced_x = np.linspace(0,1,len(x_vals[args.hyperparam])-1)
    range(len(x_vals[args.hyperparam])-1), 
    # Looping through environments
    for env_id in grouped_df['env_id'].unique():
        env_data = grouped_df[grouped_df['env_id'] == env_id]
        #plt.plot(env_data[args.hyperparam], env_data['mean_episodic_return'], marker='o', label=f'{env_id}')
        plt.plot(evenly_spaced_x, env_data['mean_episodic_return'], marker='o', label=f'{env_id}')

    
    plt.xticks(evenly_spaced_x, sorted(labels))
    plt.title("Mean Episodic Return of Varying "+x_vals[args.hyperparam][-1])
    plt.xlabel(args.hyperparam)
    plt.ylabel('Mean Episodic Return')
    plt.legend()
    plt.grid(True)

    #ax1.xaxis.set_ticks(x)

#ax2.plot(x.astype('str'), y)

    if not os.path.exists('./graphs'):
        os.mkdir('./graphs')

    plt.savefig(f"./graphs/{args.hyperparam}.png")
    plt.close
