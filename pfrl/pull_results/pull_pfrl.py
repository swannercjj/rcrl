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
mode_{mode}_base_{value}_seed_{seed}.csv
or
mode_{mode}_AR_seed_{seed}.csv

mode = {0: constant, 1: AR}
value = {baseline value like 1 or AR}
'''

@dataclass
class Args:
    entity_name: str = "rcrl"
    """Wandb workspace name."""
    project_name: str = "Learn_AR_SI_2.0"
    """Project to pull from."""
    data_dir: str = "./data_AR/"
    """The location to store cached wandb data and downloaded data."""
    data_mode: str = "table" # "graphing" # 'agg_graph' ?


def cache_runs(project_name, entity_name, data_dir):
    api = wandb.Api()
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
    # saves a csv file for graphing the episodic return
    data = data[~data['charts/episodic_return'].isnull()]
    file_path = os.path.join(data_dir, config.get('env')[4:],'graphing')
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    if config.get('mode'): #AR learning
        file_path = os.path.join(file_path,'mode_1_AR_seed_'+str(config.get('seed'))+'.csv')
    else: # baseline const
        file_path = os.path.join(file_path,'mode_0_base_'+str(config.get('action_repeat_n'))+'_seed_'+str(config.get('seed'))+'.csv')
    data.to_csv(file_path)

def agg_graph_data(data, config, data_dir):
    # fill null values with next known val?
    data = data.bfill()
    

def save_table_data(df, config, data_dir):
    # saves a csv file for making mean comparisons
    base_path = os.path.join(data_dir, config.get('env')[4:],'tables')
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    #AR learning
    file_path = os.path.join(base_path,'mode_1_AR.csv')
    df.query('mode==1').to_csv(file_path) # all the AR data
    # baseline const
    for n in df.query('mode==0')['action_repeat_n'].unique(): # different baselines
        file_path = os.path.join(base_path,'mode_0_base_'+str(n)+'.csv')
        df.query(f'mode==0 and action_repeat_n=={n}').to_csv(file_path)
    print(file_path)


def extract_data(project_name, entity_name, data_dir, data_mode):
    '''
    random notes:
    - run.history() only gives the last 500 rows of info
    - run.scan_history() gives everything, but takes forever
    - putting in keys = ['col names'] only gives columns where all vals in keys are not null
    - is this worth it rn to fix? 
    '''
    if data_mode == 'table':
        df = pd.DataFrame(columns=['env', 'seed', 'mean_episodic_return', 'mode', 'action_repeat_n'])
    api = wandb.Api()
    runs = api.runs(f"{entity_name}/{project_name}")
    for run in runs:
        cache_path = os.path.join(data_dir, f"wandb_cache/{run.id}.pkl")
        if run.state != "finished":
             continue
        config = {k:v.get('value') for k, v in json.loads(run.json_config).items()}
        print('scanning...')
        if os.path.exists(cache_path):
                #run_data_scan = pd.read_pickle(cache_path) # get rid of this for now, later problem
                run_data_scan = run.scan_history(page_size=10_000,keys=['charts/episodic_return', 'global_step', 'charts/decisions']) # TODO: might have to edit this to get the null values back on yippeeeee
                # only doing run.history() without keys give null values?
                # no_keys = run.history()
                # print(no_keys.columns)
                # new_df = no_keys[['charts/episodic_return', 'global_step', 'charts/decisions']]
                # new_df.to_csv('no_keys.csv')
                # run_data_scan.to_csv('with_keys.csv')
                info = pd.DataFrame(run_data_scan)
                info.to_csv('hi2.csv')
                input('done saving')
            
                
        else:
            run_data_scan = run.history(keys=['charts/episodic_return', 'global_step','charts/decisions']) 
            run_data_scan.to_pickle(cache_path)
        print('Done scanning.')

        data = run_data_scan 
        
        if data_mode == "table": # for replicating Marlos paper format, evaluate on the last 100 episodes
            dic = dict(data[~data['charts/episodic_return'].isnull()][-100:].mean())
            df.loc[len(df)] = [config.get('env'), config.get('seed'), dic.get('charts/episodic_return'),config.get('mode'),config.get('action_repeat_n')]

        elif data_mode == 'graphing': # making action vs decision graph
            save_graph_data(data, config, data_dir)

        else: #agg graphs?
            pass
        print(f"Data saved for run {run.id} seed {config.get('seed')}")

    if data_mode == "table":
        save_table_data(df,config,data_dir)


if __name__=="__main__":
    wandb.login()
    args = tyro.cli(Args)

    # Define where to store the files
    folder = os.path.join(args.data_dir, args.project_name)
    if not os.path.exists(folder):
        os.makedirs(folder)

    cache_runs(args.project_name, args.entity_name, folder)
    extract_data(args.project_name, args.entity_name, folder,args.data_mode)
