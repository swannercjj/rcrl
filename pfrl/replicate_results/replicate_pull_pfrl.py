import wandb
import json
import os
import pickle
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import tyro


@dataclass
class Args:
    entity_name: str = "rcrl"
    """Wandb workspace name."""
    project_name: str = "Pfrl Replicate Pong"
    """Project to pull from."""
    data_dir: str = "./data/"
    """The location to store cached wandb data and downloaded data."""
    data_name: str = "replicate_data_pfrl.csv"
    """The name of the data csv file to save"""


def cache_runs(project_name, entity_name, data_dir):
    api = wandb.Api(timeout=20)
    runs = api.runs(f"{entity_name}/{project_name}")

    cache_dir = os.path.join(data_dir, "wandb_cache/")
    
    # Define where to store the cache files
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    def process_run(job):
        (i, run) = job
    
        cache_path = os.path.join(cache_dir, f"{run.id}.pkl")
    
        # Check if we have cached data
        if not os.path.exists(cache_path):
            # collect all the data
            df = run.history()
            with open(cache_path, 'wb') as file:
                pickle.dump(df, file)
            print(f"Data cached for run: {run.id}, {i/len(runs):0.2}")
        else:
            print(f"Already cached run: {run.id}, {i/len(runs):0.2}")
    
    # Use ThreadPoolExecutor to handle the runs in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(process_run, (enumerate(runs)))


def extract_data(project_name, entity_name, data_dir):
    df = pd.DataFrame(columns=['env', 'seed', 'mean_episodic_return'])
    api = wandb.Api(timeout=20)
    runs = api.runs(f"{entity_name}/{project_name}")
    for run in runs:
        cache_path = os.path.join(data_dir, f"wandb_cache/{run.id}.pkl")
        if run.state != "finished":
            continue
    
    
        # # only wants seeds from 1-5    
        # seed_value = run.config.get('seed')  
        # if seed_value is None or seed_value not in range(1, 6):
        #     continue

        config = {k:v.get('value') for k, v in json.loads(run.json_config).items()}
    
    
        if os.path.exists(cache_path):
            run_data = pd.read_pickle(cache_path)
        else:
            run_data = run.history()
            run_data.to_pickle(cache_path)
    
        data = run_data[['charts/episodic_return']] # check if this should be charts/episodic return or eval/mean
        #data = run_data[['eval/mean']]
        # Average of the whole lifetime
        dic = dict(data[~data['charts/episodic_return'].isnull()][-100:].mean())
        #input(data[~data['charts/episodic_return'].isnull()][-100:])
        df.loc[len(df)] = [config.get('env'), config.get('seed'), dic.get('charts/episodic_return')]

        print(f"Data saved for run {run.id}")
        # os.remove(cache_path)

    file_path = os.path.join(data_dir, args.data_name)
    df.to_csv(file_path)
    # os.rmdir(os.path.join(data_dir, f"wandb_cache/"))


if __name__=="__main__":
    wandb.login()
    args = tyro.cli(Args)

    # Define where to store the files
    if not os.path.exists(args.data_dir):
        os.makedirs(args.data_dir)

    cache_runs(args.project_name, args.entity_name, args.data_dir)
    extract_data(args.project_name, args.entity_name, args.data_dir)
