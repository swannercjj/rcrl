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


@dataclass
class Args:
    project_name: str = "HyperParamSearchLr"
    """project to pull from"""
    hyperparam: str = "learning_rate"
    """desired hyperparameter to sweep"""
    cache_dir: str = "./data/wandb_cache/"
    """the location to cache wandb runs"""
    entity_name: str = "rcrl"
    """wandb workspace name"""
    file_name: str = "./data/runs.csv"


def cache_runs(project_name, entity_name, cache_dir):
    api = wandb.Api(timeout=20)
    runs = api.runs(f"{entity_name}/{project_name}")
    
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


def extract_data(project_name, entity_name, cache_dir, hyperparam):
    df = pd.DataFrame(columns=['env_id', hyperparam, 'episodic_return_average'])
    api = wandb.Api(timeout=20)
    runs = api.runs(f"{entity_name}/{project_name}")
    # data[project_name] = defaultdict(list)
    for run in runs:
        cache_path = os.path.join(cache_dir, f"{run.id}.pkl")
        if run.state != "finished":
            continue
            
        config = {k:v.get('value') for k, v in json.loads(run.json_config).items()}
    
        if config.get(hyperparam) is None:
            continue
    
        if os.path.exists(cache_path):
            run_data = pd.read_pickle(cache_path)
        else:
            run_data = run.history()
            run_data.to_pickle(cache_path)
    
        data = run_data[['charts/episodic_return']]
    
        dic = dict(data[~data['charts/episodic_return'].isnull()].mean())
        df.loc[len(df)] = [config.get('env_id'), config.get(hyperparam), dic.get('charts/episodic_return')]
        # df[config.get('env_id'), config.get('learning_rate')].append(dic.get('charts/episodic_return'))

        print(f"Data saved for run {run.id}")

    file_path = os.path.join("./data", f"{hyperparam}.csv")
    df.to_csv(file_path)


if __name__=="__main__":
    wandb.login()
    args = tyro.cli(Args)

    # Define where to store the cache files
    if not os.path.exists(args.cache_dir):
        os.makedirs(args.cache_dir)

    cache_runs(args.project_name,args.entity_name, args.cache_dir)
    extract_data(args.project_name, args.entity_name, args.cache_dir, args.hyperparam)
