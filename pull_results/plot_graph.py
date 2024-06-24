import pandas as pd
import matplotlib.pyplot as plt
import os
from dataclasses import dataclass
import tyro
import numpy as np


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

colors = {'CartPole-v1':'orange',
'Acrobot-v1':'b',
'LunarLander-v2':'g',
'MountainCar-v0':'r',
}

@dataclass
class Args:
    hyperparam: str = "tau"
    "Hyperparameter to plot."


def create_graph(hyperparam):
    file_path = os.path.join(f"./data/{hyperparam}.csv")

    if not os.path.exists(file_path):
        print(f"Data for {hyperparam} does not exist.")
        exit()

    # Read file
    df = pd.read_csv(file_path)

    # Group by 'env_id', hyperparameter and average 'mean_episodic_return'
    #grouped_df = df.groupby(['env_id', hyperparam])['mean_episodic_return'].mean().reset_index()

    # Plot the data
    plt.figure(figsize=(10, 7))
    labels = x_vals[args.hyperparam][:-1]
    
    evenly_spaced_x = np.linspace(0,1,len(x_vals[hyperparam])-1)

    for env_id in df['env_id'].unique():
        env_data = df[df['env_id'] == env_id]
        
        x_values = x_vals[hyperparam][:-1]
        y_means = []
        y_upper = []
        y_lower = []
        num_runs = len(df['seed'].unique())
        # Calculate mean and confidence intervals for each value of hyperparam
        for val in x_values:
            config_data = env_data[env_data[hyperparam] == val]
            sample_mean, _, z_statistic_std_error, upper, lower = get_CI_stats(config_data, num_runs) # maybe try putting num unique seads 
            y_means.append(sample_mean)
            y_upper.append(upper)
            y_lower.append(lower)
            

        #plt.errorbar(x_values, y_means, yerr=z_statistic_std_error, fmt='-o', label=f'Env {env_id}')
       
        plt.plot(evenly_spaced_x, y_means, marker='o', label=f'Env {env_id}', color=colors[env_id])
        plt.fill_between(evenly_spaced_x, y_lower, y_upper, alpha=0.1, color=colors[env_id])
       
    
        
    
    plt.xticks(evenly_spaced_x, sorted(labels))
    plt.title("Mean Episodic Return of Varying "+x_vals[hyperparam][-1])
    plt.xlabel(hyperparam, labelpad=20)
    plt.ylabel('Mean Episodic Return')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=5)
    plt.grid(True)



    if not os.path.exists('./graphs'):
        os.mkdir('./graphs')

    plt.savefig(f"./graphs/{hyperparam}.png")
    plt.close

def get_CI_stats(data, num_runs):
    sample_mean = np.mean(data['mean_episodic_return'])
    sample_std = np.std(data['mean_episodic_return'], axis=0, ddof=1)
    z_statistic_std_error = 1.96 * sample_std/np.sqrt(num_runs)
    upper, lower = sample_mean + z_statistic_std_error, sample_mean - z_statistic_std_error
    return sample_mean, sample_std, z_statistic_std_error, upper, lower

if __name__=="__main__":
    args = tyro.cli(Args)
    create_graph(args.hyperparam)


