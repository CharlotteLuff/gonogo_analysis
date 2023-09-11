# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 16:33:13 2023
Go no go analysis functions
@author: cluff
"""
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def get_array(lines,indx):
    # Locate the index of the line
    line_index = lines.index(indx)
    # Get the line as a string
    line = lines[line_index + 1]
    # Split the line into tokens
    tokens = line.split()
    # Convert tokens to floats and create a numpy array
    B_array = np.array([float(token) for token in tokens[1:-2]])
    return B_array

def get_arrays(lines,no_columns,start,end):
    # Process the lines from start section to end section to create numerical arrays
    # Find the index where the "D:" section starts
    start_section_index = lines.index(start)
    # Find the index where the "E:" section starts
    end_section_index = lines.index(end)


    data_arrays = []
    trial_no = []

    for line in lines[start_section_index + 1 : end_section_index]:
        # Remove leading and trailing whitespace, split the line into tokens, and convert to floats
        tokens = line.strip().split()
        if tokens:
            data_array = np.array([float(token) for token in tokens[1:]])
            data_arrays.append(data_array[1:no_columns+1])  # Exclude the first element (trial number)
            trial_no.append(data_array[0])
    return data_arrays, trial_no

def get_pcrr(D_arrays,F_arrays):
    
    # PreCue Response Rate = NosePokes during all PreCue periods in one session (D(J+2)) / total duration of PreCues in that session (F(G+4))
    # (D(J+2)) = index 1 in our arrays, (F(G+4)) = index 3 in our arrays
    pc_nosepokes = []
    pc_durations = []

    for trial in D_arrays:
        pc_nosepokes.append(trial[1])   
    for trial in F_arrays:
        pc_durations.append(trial[3])
        
    # Convert data_arrays to a NumPy array
    pc_nosepokes = np.array(pc_nosepokes)
    pc_durations = np.array(pc_durations)
    # Sum the arrays element-wise
    sum_pc_nosepokes = np.sum(pc_nosepokes, axis=0)
    sum_pc_durations = np.sum(pc_durations, axis=0)

    pc_rr = sum_pc_nosepokes/(sum_pc_durations/60)
    
    return pc_rr

def get_laser_cond_arrays(D_arrays,F_arrays):
        
    D_laser_cond_arrays = {}
    F_laser_cond_arrays = {}
    
    for i in range(len(D_arrays)):
        group_number = int(D_arrays[i][-1])  # Get the last element as the group number
        if group_number not in D_laser_cond_arrays:
            D_laser_cond_arrays[group_number] = []
        D_laser_cond_arrays[group_number].append(D_arrays[i])
        if group_number not in F_laser_cond_arrays:
            F_laser_cond_arrays[group_number] = []
        F_laser_cond_arrays[group_number].append(F_arrays[i])

    return D_laser_cond_arrays, F_laser_cond_arrays

def get_trial_type(D_laser_cond_arrays, F_laser_cond_arrays):
    
    D_laser_go_trials = [[] for _ in range(len(D_laser_cond_arrays))]
    D_laser_no_go_trials = [[] for _ in range(len(D_laser_cond_arrays))]
    F_laser_go_trials = [[] for _ in range(len(F_laser_cond_arrays))]
    F_laser_no_go_trials = [[] for _ in range(len(F_laser_cond_arrays))]
    
    for i in range(len(D_laser_cond_arrays)):
        for j, trial in enumerate(D_laser_cond_arrays[i]):
            if trial[2] == 2 and trial[4] != 0:
                D_laser_go_trials[i].append(trial)
                F_laser_go_trials[i].append(F_laser_cond_arrays[i][j])
            elif trial[2] == 2 and trial[6] != 0:
                D_laser_no_go_trials[i].append(trial)
                F_laser_no_go_trials[i].append(F_laser_cond_arrays[i][j])
    
    return D_laser_go_trials, D_laser_no_go_trials, F_laser_go_trials, F_laser_no_go_trials


def get_laser_corrects(laser_go_trials, laser_no_go_trials):

    correct_go = [[] for _ in range(len(laser_go_trials))]
    percent_correct_go = [[] for _ in range(len(laser_go_trials))]
        
    for i in range(len(laser_go_trials)):
        matching_arrays = [arr for arr in laser_go_trials[i] if arr[4] == 2]
        correct_go[i].extend(matching_arrays)
        if len(laser_go_trials[i]) != 0:
            percent_correct_go[i] = len(correct_go[i]) / len(laser_go_trials[i]) * 100
        else:
            percent_correct_go[i] = float('nan')
                
        correct_no_go = [[] for _ in range(len(laser_go_trials))]
        percent_correct_no_go = [[] for _ in range(len(laser_go_trials))]
            
    for i in range(len(laser_no_go_trials)):
        matching_arrays = [arr for arr in laser_no_go_trials[i] if arr[6] == 2]
        correct_no_go[i].extend(matching_arrays)
        if len(laser_no_go_trials[i]) != 0:
            percent_correct_no_go[i] = len(correct_no_go[i]) / len(laser_no_go_trials[i]) * 100
        else:
            percent_correct_no_go[i] = float('nan')  
                
    return percent_correct_go, percent_correct_no_go

def get_latencies(D_laser_no_go_trials,F_laser_no_go_trials):
    
    latencies = [[] for _ in range(len(D_laser_no_go_trials))]
    
    for i in range(len(D_laser_no_go_trials)):
        for j, arr in enumerate(D_laser_no_go_trials[i]):
            if arr[6] == 1:
                latencies[i].append(F_laser_no_go_trials[i][j][6])
    return latencies

def get_mean_latencies(latencies):
    
    mean_latencies = []
    
    for i in range(len(latencies)):
       mean_latencies.append(np.mean(latencies[i]))
       
    return mean_latencies
                
def get_laser_pcrr(D_laser_cond_arrays, F_laser_cond_arrays):
    lasers_pc_rr = {}

    pc_nosepokes = {}
    pc_durations = {}
    sum_pc_nosepokes = {}
    sum_pc_durations = {}

    for i in range(len(D_laser_cond_arrays)):
        pc_nosepokes[i] = []
        pc_durations[i] = []

        for trial in D_laser_cond_arrays[i]:
            pc_nosepokes[i].append(trial[1])
        for trial in F_laser_cond_arrays[i]:
            pc_durations[i].append(trial[3])

        pc_nosepokes[i] = np.array(pc_nosepokes[i])
        pc_durations[i] = np.array(pc_durations[i])
        sum_pc_nosepokes[i] = np.sum(pc_nosepokes[i], axis=0)
        sum_pc_durations[i] = np.sum(pc_durations[i], axis=0)

        lasers_pc_rr[i] = sum_pc_nosepokes[i] / (sum_pc_durations[i] / 60)

    return lasers_pc_rr

def get_laser_gorr(D_laser_cond_arrays, F_laser_cond_arrays):
    lasers_go_rr = {}

    go_nosepokes = {}
    go_durations = {}
    sum_go_nosepokes = {}
    sum_go_durations = {}

    target_indices = [0, 2]

    for i in target_indices:
        go_nosepokes[i] = []
        go_durations[i] = []

        for trial in D_laser_cond_arrays[i]:
            go_nosepokes[i].append(trial[3])
        for trial in F_laser_cond_arrays[i]:
            go_durations[i].append(trial[5])

        go_nosepokes[i] = np.array(go_nosepokes[i])
        go_durations[i] = np.array(go_durations[i])
        sum_go_nosepokes[i] = np.sum(go_nosepokes[i], axis=0)
        sum_go_durations[i] = np.sum(go_durations[i], axis=0)

        lasers_go_rr[i] = sum_go_nosepokes[i] / (sum_go_durations[i] / 60)
        
    return lasers_go_rr

def get_laser_nogorr(D_laser_cond_arrays, F_laser_cond_arrays):
    lasers_nogo_rr = {}

    nogo_nosepokes = {}
    nogo_durations = {}
    sum_nogo_nosepokes = {}
    sum_nogo_durations = {}

    target_indices = [0, 3]

    for i in target_indices:
        nogo_nosepokes[i] = []
        nogo_durations[i] = []

        for trial in D_laser_cond_arrays[i]:
            nogo_nosepokes[i].append(trial[5])
        for trial in F_laser_cond_arrays[i]:
            nogo_durations[i].append(trial[7])

        nogo_nosepokes[i] = np.array(nogo_nosepokes[i])
        nogo_durations[i] = np.array(nogo_durations[i])
        sum_nogo_nosepokes[i] = np.sum(nogo_nosepokes[i], axis=0)
        sum_nogo_durations[i] = np.sum(nogo_durations[i], axis=0)

        lasers_nogo_rr[i] = sum_nogo_nosepokes[i] / (sum_nogo_durations[i] / 60)
        
    return lasers_nogo_rr

def get_percent_pc_failure(D_laser_cond_arrays):
    
    percent_pc_failure = [[] for _ in range(len(D_laser_cond_arrays))]
    
    for i in range(len(D_laser_cond_arrays)):
        for ii in range(len(D_laser_cond_arrays[i])):
            matching_arrays = [arr for arr in D_laser_cond_arrays[i] if arr[2] == 1]
            percent_pc_failure[i] = len(matching_arrays) / len(D_laser_cond_arrays[i]) * 100
            
    return percent_pc_failure
        
def get_avg_laser_results(results):
    # Initialize a dictionary to store mean laser results
    avg_laser_results = defaultdict(dict)
    
    # List of laser-related metrics to average
    laser_metrics = ["laser_pc_rr", "laser_go_rr", "laser_nogo_rr"]
    
    # Iterate through laser metrics
    for metric in laser_metrics:
        metric_averages = {}
        
        # Iterate through conditions and their laser results
        for condition_name, condition_results in results.items():
            metric_list = []
            for animal_id, animal_results in condition_results.items():
                metric_list.append(animal_results[metric])
            
            metric_means = {}
            metric_stds = {}
            
            # Iterate through the keys in the sub-dictionaries
            for key in metric_list[0].keys():
                values = [animal[key] for animal in metric_list]
                metric_means[key] = np.mean(values)
                metric_stds[key] = np.std(values)
            
            metric_averages[condition_name] = {
                "mean": metric_means,
                "std": metric_stds
            }
        
        # Store the metric averages in the dictionary
        avg_laser_results[metric] = metric_averages
    return avg_laser_results
    
def get_avg_results(results):
    # List of metrics to average
    metrics = ["pc_rr", "correct_go_rr", "correct_nogo_rr"]

    # Initialize dictionaries to store mean results and metric lists
    avg_results = defaultdict(dict)
    metric_lists = defaultdict(dict)

    # Iterate through metrics
    for metric in metrics:
        metric_averages = {}
        metric_list_arrays = []

        # Iterate through conditions and their results
        for condition_name, condition_results in results.items():
            metric_list = []
            for animal_id, animal_results in condition_results.items():
                metric_list.append(animal_results[metric])
            
            metric_list_arrays.append(metric_list)
            
            metric_avg = np.mean(metric_list)
            metric_std = np.std(metric_list)
            
            metric_averages[condition_name] = {
                "mean": metric_avg,
                "std": metric_std
            }
        
        # Store the metric averages and lists in the dictionaries
        avg_results[metric] = metric_averages
        metric_lists[metric] = metric_list_arrays
        
    return avg_results, metric_lists

def graphics_settings(color):
    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = ['Arial']
    plt.rcParams['font.size'] = 12
    if color == 0:
        sns.set_palette('cividis_r')
    elif color == 1:
        sns.set_palette('summer_r')
    elif color == 2:
        sns.set_palette('Set3_r')
    if color == 3:
        sns.set_palette('BuGn_r')
    elif color == 4:
        sns.set_palette('PuBu_r')
    elif color == 5:
        sns.set_palette('PuRd_r')
    elif color == 6:
        sns.set_palette('BuPu_r')

def grouped_boxplot(xx,yy,mydata,zz=None,ylim=None,title=None):

    plt.figure()
    ax = sns.boxplot(x=xx, y=yy, hue=zz, data=mydata,flierprops={"marker": "+"})
    sns.stripplot(x=xx, y=yy, hue=zz, data=mydata, dodge=True, jitter=True, alpha=0.7, palette='dark:black',legend=False)
    
    #sns.despine(offset=10, trim=True)
    #ax.axhline(y=0, linestyle='--', color='0.7', zorder=0)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if ylim is not None:
        ax.set_ylim(ylim)  # Set y-axis limits if ylim is provided
        
    if title is not None:
        plt.title(title)  # Set the title if provided
        
        plt.tight_layout()  

def get_rates_data(results, measure_key, measure_label):
    y = []
    conditions = []
    measures = []
    
    for condition_name, condition_results in results.items():
        for animal_id, animal_results in condition_results.items():
            temp = animal_results[measure_key]
            y.append(temp)
            conditions.extend([condition_name])
            measures.extend([measure_label])
            
    return y, conditions, measures

def get_probs_data(results, measure, measure1, measure_label, measure1_label):
    y = []
    conditions = []
    measures = []

    for condition_name, condition_results in results.items():
        for animal_id, animal_results in condition_results.items():
            temp1 = animal_results[measure]
            y.append(temp1)
            temp2 = animal_results[measure1] 
            y.append(temp2)
            conditions.extend([condition_name] * 2)
            measures.extend([measure_label, measure1_label])  
        
    return y, conditions, measures  # Changed measures to measure_labels

def get_laser_data(results, measure, all_lasers, specific_lasers=None):

    y = []
    conditions = []
    laser_labels = []
    
    # Define the specific laser conditions you want to plot
    specific_laser_conditions = specific_lasers  # Add the condition names you want to plot here
    if specific_lasers is not None:
        
        for condition_name, condition_results in results.items():
            for animal_id, animal_results in condition_results.items():
                temp = animal_results[measure]
                y.extend(temp)
                conditions.extend([condition_name] * len(temp))
                laser_labels.extend(all_lasers)
        
       
            # Filter the data based on specific laser conditions
            specific_laser_indices = [i for i, label in enumerate(laser_labels) if label in specific_laser_conditions]
            filtered_conditions = [conditions[i] for i in specific_laser_indices]
            filtered_y = [y[i] for i in specific_laser_indices]
            filtered_labels = [laser_labels[i] for i in specific_laser_indices]
            
        return filtered_y, filtered_conditions, filtered_labels
    
    else:
        
        for condition_name, condition_results in results.items():
            for animal_id, animal_results in condition_results.items():
                temp = animal_results[measure].values()
                y.extend(temp)  # Extend the list with each element of laser_pc_rr
                conditions.extend([condition_name] * len(temp))  # Append condition_name for each element
                laser_labels.extend(all_lasers)  
        
        return y, conditions, laser_labels

def get_dataframe(df_variables):
    dataframe_data = pd.DataFrame(df_variables)
    
    return dataframe_data


    
