# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 15:55:51 2023
GoNoGO analysis
@author: cluff
"""

from gonogo_functions import *
plt.close('all')

sweep = 0
graphics_settings(sweep)

results = {}
Ddata = {}
filenames = {}

condition_names = ["Opto", "BI", "Chemo"]
animal_ids = ["NP98", "NP102", "NP129", "NP152", "TR153","TR242"]

filenames[0] = ['OptoTestNP98.txt','OptoTestNP102.txt','OptoTestNP129.txt','OptoTestNP152.txt','OptoTestTR153.txt','OptoTestTR242.txt'] #Opto
filenames[1] = ['BIOptoTestNP98.txt','BIOptoTestNP102.txt','BIOptoTestNP129.txt','BIOptoTestNP152.txt','BIOptoTestTR153.txt','BIOptoTestTR242.txt'] #BI
filenames[2] = ['ChemoOptoTestNP98.txt','ChemoOptoTestNP102.txt','ChemoOptoTestNP129.txt','ChemoOptoTestNP152.txt','ChemoOptoTestTR153.txt','ChemoOptoTestTR242.txt'] #Chemo

for condition in range(len(filenames)):
    condition_name = condition_names[condition]
    Ddata[condition_name] = {} 
    results[condition_name] = {} 
    for animal in range(len(filenames[condition])):
        animal_id = animal_ids[animal]
        filename = filenames[condition][animal]
        file_path = ('C:\\Users\\cluff\\Documents\\PYTHON\\Gonogo_analysis\\' + filename)     # CHANGE PATH HERE
        
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Extract data
        
        B_array = get_array(lines, "B:\n")
        D_arrays, trial_no = get_arrays(lines, 9, "D:\n", "E:\n")
        F_arrays, trial_no = get_arrays(lines, 10, "F:\n", "L:\n")
        
        # Create dictionaries to store separated arrays
        
        D_laser_cond_arrays, F_laser_cond_arrays = get_laser_cond_arrays(D_arrays, F_arrays)
        
        # Check premature response rate
        
        percent_pc_failure = get_percent_pc_failure(D_laser_cond_arrays)

        # Separate go and no go trials- put into function
        D_laser_go_trials, D_laser_no_go_trials, F_laser_go_trials, F_laser_no_go_trials = get_trial_type(D_laser_cond_arrays,F_laser_cond_arrays)
        percent_correct_go, percent_correct_no_go = get_laser_corrects(D_laser_go_trials, D_laser_no_go_trials)
        latencies = get_latencies(D_laser_no_go_trials,F_laser_no_go_trials)  
        mean_latencies = get_mean_latencies(latencies)
        
        # Compute overall response rate
        
        pc_rr = get_pcrr(D_arrays, F_arrays)
        
        # Compute correct probability
        correct_go_prob = B_array[6] / B_array[3] *100
        correct_nogo_prob = B_array[9] / B_array[4] * 100
        
        # Compute laser condition response rates
        
        laser_pc_rr = get_laser_pcrr(D_laser_cond_arrays, F_laser_cond_arrays)
        
        # Store the data in the dictionary
        Ddata[condition_name][animal_id] = {
            "laser_go_trials": D_laser_go_trials,
            "laser_no_go_trials": D_laser_no_go_trials,
            "D_laser_cond_arrays": D_laser_cond_arrays}
        
        # Store the results in the dictionary
        results[condition_name][animal_id] = {
            "pc_rr": pc_rr,
            "correct_go_prob": correct_go_prob,
            "correct_nogo_prob": correct_nogo_prob,
            "laser_pc_rr": laser_pc_rr,
            "laser_percent_correct_go": percent_correct_go,
            "laser_percent_correct_nogo": percent_correct_no_go,
            "percent_pc_failure": percent_pc_failure,
            "mean_latencies": mean_latencies}

# Plotting 

y, conditions, laser_labels = get_laser_data(results, 'laser_pc_rr', ["No laser", "Pre cue laser", "Go laser","No go laser"])                      
laser_pcrr_df = get_dataframe({'Laser condition': laser_labels, 'Condition': conditions, 'Rate': y})
grouped_boxplot('Laser condition', 'Rate', laser_pcrr_df, 'Condition')
plt.title('Pre Cue Response Rate by Laser Condition')

y, conditions, measures = get_rates_data(results,'pc_rr',"Pre cue response rate")
pc_rr_df = get_dataframe({'Measure': measures, 'Condition': conditions, 'Rate': y})
grouped_boxplot('Measure','Rate',pc_rr_df,'Condition',ylim=(0, 5),title='Pre Cue Response Rates')

graphics_settings(1)
y, conditions, measures = get_probs_data(results,'correct_go_prob','correct_nogo_prob',"Correct go", "Correct no go")
probs_df = get_dataframe({'Measure': measures, 'Condition': conditions, 'Probability (%)': y})
grouped_boxplot('Measure','Probability (%)',probs_df,'Condition',ylim=(0, 105),title='Correct Probability')

graphics_settings(2)
filtered_y, filtered_conditions, filtered_labels = get_laser_data(results,'laser_percent_correct_go',["No laser", "Pre cue laser", "Go laser", "No go laser"],["No laser","Go laser"])
go_percents_df = get_dataframe({'Laser condition': filtered_labels, 'Condition': filtered_conditions, 'Probability (%)': filtered_y})
grouped_boxplot('Laser condition', 'Probability (%)', go_percents_df, 'Condition', ylim=(0, 105), title='Correct Go Trial Probability')

filtered_y, filtered_conditions, filtered_labels = get_laser_data(results,'laser_percent_correct_nogo',["No laser", "Pre cue laser", "Go laser", "No go laser"],["No laser","No go laser"])
nogo_percents_df = get_dataframe({'Laser condition': filtered_labels, 'Condition': filtered_conditions, 'Probability (%)': filtered_y})
grouped_boxplot('Laser condition', 'Probability (%)', nogo_percents_df, 'Condition', ylim=(0, 105), title='Correct No Go Trial Probability')

graphics_settings(3)
filtered_y, filtered_conditions, filtered_labels = get_laser_data(results,'percent_pc_failure',["No laser", "Pre cue laser", "Go laser", "No go laser"],["No laser","Pre cue laser"])
pc_failure_percents_df = get_dataframe({'Laser condition': filtered_labels, 'Condition': filtered_conditions, 'Probability (%)': filtered_y})
grouped_boxplot('Laser condition', 'Probability (%)', pc_failure_percents_df, 'Condition', ylim=(-10, 105), title='Pre Cue Failure Probability')

graphics_settings(4)
filtered_y, filtered_conditions, filtered_labels = get_laser_data(results,'mean_latencies',["No laser", "Pre cue laser", "Go laser", "No go laser"],["No laser", "No go laser"])
nogo_latencies_df = get_dataframe({'Laser condition': filtered_labels, 'Condition': filtered_conditions, 'Mean Latency (s)': filtered_y})
grouped_boxplot('Laser condition', 'Mean Latency (s)', nogo_latencies_df, 'Condition',ylim=(-1, 10), title='Latency To Nose Poke (Incorrect No Go Trials)')
