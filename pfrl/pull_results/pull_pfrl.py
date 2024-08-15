import wandb
import json
import os
import pickle
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import tyro


'''
Name Format:
{mode}_{value}_{seed}.csv

mode = {0: constant, 1: AR}
value = {baseline value like 1 or AR}

ex) mode_0_val_1_seed_1.csv or mode_1_AR_seed_1.csv

'''

@dataclass
class Args:
    entity_name: str = "rcrl"
    """Wandb workspace name."""
    project_name: str = "Learn_AR"
    """Project to pull from."""
    data_dir: str = "./data/"
    """The location to store cached wandb data and downloaded data."""
    data_mode: str = "graph" # "mean"


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

def save_graph_data(data, config, data_dir):
    # mode_1_AR_seed_1.csv 
    data = data[~data['charts/episodic_return'].isnull()]
    file_path = os.path.join(data_dir, config.get('env')[4:])
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    if config.get('mode'): #AR learning
        file_path = os.path.join(file_path,'mode_1_AR_seed_'+str(config.get('seed'))+'.csv')
    else: # baseline const
        file_path = os.path.join(file_path,'mode_0_base_'+str(config.get('action_repeat_n'))+'_seed_'+str(config.get('seed'))+'.csv')
    data.to_csv(file_path)


def extract_data(project_name, entity_name, data_dir):
    if args.data_mode == 'mean':
        df = pd.DataFrame(columns=['env', 'seed', 'mean_episodic_return'])
    api = wandb.Api(timeout=20)
    runs = api.runs(f"{entity_name}/{project_name}")
    for run in runs:
        cache_path = os.path.join(data_dir, f"wandb_cache/{run.id}.pkl")
        if run.state != "crashed":
            continue
        config = {k:v.get('value') for k, v in json.loads(run.json_config).items()}
        # if config.get('mode') != 0: #only want mode 0/ const repeats
        #     continue
        
        if os.path.exists(cache_path):
            run_data = pd.read_pickle(cache_path)
        else:
            run_data = run.history()
            run_data.to_pickle(cache_path)
    
        print(config)

        data = run_data[['charts/episodic_return', 'global_step']]

        if args.data_mode == "mean": # for replicating Marlos paper format, evaluate on the last 100 episodes
            dic = dict(data[~data['charts/episodic_return'].isnull()][-100:].mean())
            df.loc[len(df)] = [config.get('env'), config.get('seed'), dic.get('charts/episodic_return')]
        else: # making action vs decision graph
            if config.get('mode')==1:
                save_graph_data(data, config, data_dir)
        print(f"Data saved for run {run.id} seed {config.get('seed')}")

    if args.data_mode == "mean":
        file_path = os.path.join(data_dir,config.get('env'), args.data_name+'.csv')
        df.to_csv(file_path)


if __name__=="__main__":
    wandb.login()
    args = tyro.cli(Args)

    # Define where to store the files
    if not os.path.exists(args.data_dir):
        os.makedirs(args.data_dir)

    cache_runs(args.project_name, args.entity_name, args.data_dir)
    extract_data(args.project_name, args.entity_name, args.data_dir)
