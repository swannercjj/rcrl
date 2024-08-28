import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from dataclasses import dataclass
import tyro

styles = {
    'Baseline_1': {'color': 'orange', 'linestyle': '-'},        # Lots of dots
    'Baseline_4': {'color': 'red', 'linestyle': '-'},           # Dot-dash pattern
    'Baseline_16': {'color': 'green', 'linestyle': '-'},        # Dashes
    'Baseline_64': {'color': 'purple', 'linestyle': '-'},        # Solid line
    'Action_Repeats': {'color': 'blue', 'linestyle': '-'}       # Dot-dash pattern
}

@dataclass
class Args:
    data_dir: str = "./data_AR/"
    data_env: str = "SpaceInvaders-v5"
    project_name: str = "Learn_AR_SI_2.0"
    save_dir: str = './results_AR/'
    x_axis: str = 'decisions' #global_step
    avg_graph: bool = True 

def list_files(data_path):
    baselines = {}
    ar = []
    for file in os.listdir(data_path):
        mode = int(file.split('_')[1])
        seed = file.split('_')[-1].replace('.csv', '')
        
        if mode == 0: 
            value = file.split('_')[3]
            if value not in baselines:
                baselines[value] = [os.path.join(data_path, file)]
            else:
                baselines[value].append(os.path.join(data_path, file))
        
        elif mode == 1:
            ar.append(os.path.join(data_path, file))

    return baselines, ar

def load_data(files):
    data = []
    x_values = []
    for file in files:
        df = pd.read_csv(file)
        data.append(df['charts/episodic_return'].values)
        axis = 'charts/decisions' if args.x_axis == 'decisions' else 'global_step'
        x_values.append(df[axis].values)

    
    return np.array(data, dtype="object"), np.array(x_values, dtype="object")

def plot_graphs(ax, data, x_values, style, label):
    mean_y = np.mean(data, axis=0,dtype=float)
    mean_x = np.mean(x_values, axis=0,dtype=float)
    std_error = np.std(data.astype(int), axis=0) / np.sqrt(data.shape[0])
    
    # # plotting individual runs in the background
    # for i in range(data.shape[0]):
    #     ax.plot(x_values[i], data[i], color=style['color'], linestyle=style['linestyle'], alpha=0.1)
    

    ax.plot(mean_x, mean_y, color=style['color'], linestyle=style['linestyle'], label=label, linewidth=2)
    ax.fill_between(mean_x, (mean_y - 1.96 * std_error).astype(float), (mean_y + 1.96 * std_error).astype(float), color=style['color'], alpha=0.3)

if __name__ == "__main__":
    args = tyro.cli(Args)
    graph_type = 'avg_graphing' if args.avg_graph == True else 'graphing'
    data_path = os.path.join(args.data_dir, args.project_name, args.data_env, graph_type)
    save_folder = os.path.join(args.save_dir, args.project_name, args.data_env, 'avg_graphs' if args.avg_graph == True else 'graphs')
    
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    baselines, ar = list_files(data_path)
    
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))

    for value, files in baselines.items():
        if value  == '4':
            continue
        baseline_data, x_values = load_data(files)
        plot_graphs(ax, baseline_data, x_values, styles[f'Baseline_{value}'], f'Repeat - {value}')
    
    ar_data, ar_x_values = load_data(ar)
    plot_graphs(ax, ar_data, ar_x_values, styles['Action_Repeats'], 'Action Repeats')
    
    x_label = 'Decsions' if args.x_axis == 'decisions' else 'Global Step'
    ax.set_xlabel(x_label)
    ax.set_ylabel('Episodic Return')
    ax.set_title(f'{args.data_env} - Comparison of Action Repeats as a Hyperparameter and Learning Action Repeats')
    ax.legend()
    
    plt.savefig(os.path.join(save_folder, f'comparison_plot_{args.x_axis}.png'))
    print(os.path.join(save_folder, f'comparison_plot_{args.x_axis}.png'))
    plt.show()
