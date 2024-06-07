import wandb
import json
import os
import pickle
from collections import defaultdict
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from dataclasses import dataclass
import tyro

PROJECTS = [
    "CartPole_Trials2.0",
    "Acrobot_trials2.0",
]


@dataclass
class Args:
    cache_dir: str = "./data/wandb_cache/"
    """the location to cache wandb runs"""
    entity_name: str = "rcrl"
    """wandb workspace name"""
    file_name: str = "./data/runs.csv"


def cache_runs(entity_name):
    for project_name in PROJECTS:
        api = wandb.Api(timeout=20)
        runs = api.runs(f"{entity_name}/{project_name}")
        
        # Define where to store the cache files
        cache_dir = "./wandb_cache/"
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
            # else:
            #     print(f"Already cached run: {run.id}, {i/len(runs):0.2}")
        
        # Use ThreadPoolExecutor to handle the runs in parallel
        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(process_run, (enumerate(runs)))


def extract_data(entity_name, cache_dir, file_name):
    for project_name in PROJECTS:
        data = defaultdict(dict)
        api = wandb.Api(timeout=20)
        runs = api.runs(f"{entity_name}/{project_name}")
        data[project_name] = defaultdict(list)
        for run in runs:
            cache_path = os.path.join(cache_dir, f"{run.id}.pkl")
            if run.state != "finished":
                # print(cache_path)
                continue
                
            config = {k:v.get('value') for k, v in json.loads(run.json_config).items()}
        
            if config.get('async_datarate') is None:
                continue
        
            if os.path.exists(cache_path):
                run_df = pd.read_pickle(cache_path)
            else:
                run_df = run.history()
                run_df.to_pickle(cache_path)
        
            df = run_df[['charts/episodic_return']]
        
            dic = dict(df[~df['charts/episodic_return'].isnull()].mean())
        
            data[project_name][config.get('learning_rate')].append(dic.get('charts/episodic_return'))

    df = pd.DataFrame(data)
    df.to_csv(file_name)


if __name__=="__main__":
    wandb.login()
    args = tyro.cli(Args)
    print(args)
    print(PROJECTS)

    # Define where to store the cache files
    if not os.path.exists(args.cache_dir):
        os.makedirs(args.cache_dir)

    cache_runs(args.entity_name)
    extract_data(args.entity_name, args.cache_dir, args.file_name)
