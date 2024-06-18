import pandas as pd
import matplotlib.pyplot as plt
import os
from dataclasses import dataclass
import tyro


@dataclass
class Args:
    hyperparam: str = "learning_rate"
    "Hyperparameter to plot."


if __name__=="__main__":
    args = tyro.cli(Args)

    file_path = os.path.join(f"./data/{args.hyperparam}.csv")

    if not os.path.exists(file_path):
        print(f"Data for {args.hyerparam} does not exist.")
        exit()

    # Read file
    df = pd.read_csv(file_path)

    # Group by 'env_id', hyperparameter and average 'mean_episodic_return'
    grouped_df = df.groupby(['env_id', args.hyperparam])['mean_episodic_return'].mean().reset_index()

    # Plot the data
    plt.figure(figsize=(10, 6))

    # Looping through environments
    for env_id in grouped_df['env_id'].unique():
        env_data = grouped_df[grouped_df['env_id'] == env_id]
        plt.plot(env_data[args.hyperparam], env_data['mean_episodic_return'], marker='o', label=f'{env_id}')

    plt.xlabel(args.hyperparam)
    plt.ylabel('mean_episodic_return')
    plt.legend()
    plt.grid(True)

    if not os.path.exists('./graphs'):
        os.mkdir('./graphs')

    plt.savefig(f"./graphs/{args.hyperparam}.png")
