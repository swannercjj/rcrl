import os
import numpy as np
import pandas as pd

'''
Make a new csv file of game | episodic return with the standard deviation (Have yet to saving to csv)
'''


def get_CI_stats(data, num_runs):
    sample_mean = np.mean(data['mean_episodic_return'])
    sample_std = np.std(data['mean_episodic_return'])
    z_statistic_std_error = 1.96 * sample_std/np.sqrt(num_runs)
    upper, lower = sample_mean + z_statistic_std_error, sample_mean - z_statistic_std_error
    return sample_mean, sample_std, z_statistic_std_error, upper, lower



def log_info(df):
    data = []
    for env_id in df['env_id'].unique():
        env_data = df[df['env_id'] == env_id]
        runs = len(env_data)
        sample_mean, sample_std, z_statistic_std_error, upper, lower = get_CI_stats(env_data, runs)
        data.append([env_id, str(sample_mean)+' ('+str(z_statistic_std_error)+')',runs])
    return data


file_path = os.path.join(f"./data/replicate_data.csv")
df = pd.read_csv(file_path)
data = log_info(df)
new_df = pd.DataFrame(data, columns=['Game', 'Mean Episodic Return', "Num Runs"])

print(new_df)
#data_dir = "./results/" 
file_path = os.path.join("./data/", f"replicate_results.csv")  
new_df.to_csv(file_path)

'''
- hypers double check
- code
'''
