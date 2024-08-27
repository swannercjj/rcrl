import pandas as pd
import os
from dataclasses import dataclass
import tyro

'''Creates rolling/window avg from graphing csv files'''

@dataclass
class Args:
    data_dir: str = "./data_AR/"
    data_env: str = "SpaceInvaders-v5"
    project_name: str = "Learn_AR_SI_2.0"
    save_dir: str = 'avg_graphing'  
    window: int = 25


def avg_data(folder, window=25):
    data_path = os.path.join(args.data_dir, args.project_name, args.data_env, 'graphing')
    for file in os.listdir(data_path):
        df = pd.read_csv(os.path.join(data_path,file))
        df['charts/episodic_return'] = df['charts/episodic_return'].rolling(window=window).mean()
        df.dropna(subset=['charts/episodic_return'], inplace=True)
        # make a new folder for avg_graphing
        save_path = os.path.join(folder, file) # same name but different folder
        df.to_csv(save_path, index=False)



if __name__=="__main__":

    args = tyro.cli(Args)

    # Define where to store the files
    folder = os.path.join(args.data_dir, args.project_name, args.data_env, args.save_dir)
    if not os.path.exists(folder):
        os.makedirs(folder)

    avg_data(folder, 25)

