import os
import numpy as np
import pandas as pd
from dataclasses import dataclass
import tyro

'''
Make a new csv file of game | episodic return with the standard deviation (Have yet to saving to csv)
'''

@dataclass
class Args:
    data_dir: str = "./data_AR/"
    """The location to store cached wandb data and downloaded data."""
    data_env: str = "SpaceInvaders-v5"
    project_name: str = "Learn_AR_2.0"
    save_dir: str = './results_AR/'
  

def get_CI_stats(data, num_runs):
    sample_mean = np.mean(data['mean_episodic_return'])
    sample_std = np.std(data['mean_episodic_return'])
    z_statistic_std_error = 1.96 * sample_std/np.sqrt(num_runs)
    upper, lower = sample_mean + z_statistic_std_error, sample_mean - z_statistic_std_error
    return sample_mean, sample_std, z_statistic_std_error, upper, lower


def log_info(df):
    data = []
    for env_id in df['env'].unique():
        env_data = df[df['env'] == env_id]
        runs = len(env_data)
        sample_mean, sample_std, z_statistic_std_error, upper, lower = get_CI_stats(env_data, runs)
        data.append([env_id, str(sample_mean)+' ('+str(z_statistic_std_error)+')',runs])
    return data


if __name__=="__main__":
    args = tyro.cli(Args)
    data_path = os.path.join(args.data_dir,args.project_name,args.data_env,'tables')
    # input(os.listdir(data_path))
    save_folder = os.path.join(args.save_dir,args.project_name,args.data_env,'tables')
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    for file in os.listdir(data_path):
        df = pd.read_csv(os.path.join(data_path,file))
        data = log_info(df)
        new_df = pd.DataFrame(data, columns=['Game', 'Mean Episodic Return', "Num Runs"])
        print(new_df)
        file_path = os.path.join(save_folder, str(file)[:-4]+'_results.csv')  
        new_df.to_csv(file_path)
        print(data,'saved in', file_path)
        
   
    

