import os
import sys
import pandas as pd

# ----------
# overhead
# ----------
rootdir='/my_path/my_study_dataset'
# get list of subjects
subs = pd.read_csv(rootdir, 'participants.tsv'), sep='\t', dtype={'id': str})

task_list=['mytask1']

# provide total length of task in seconds
# excluding any additional time for waiting for the scanner sync
length_tasks = {'mytask1': 480, \
'mytask2': 600, \
}

conditions_mytask1 = {'ev1': 'move right hand', \
'ev1': 'move left hand', \
'ev3': 'move right foot', \
'ev4': 'move left foot', \
'no_ev': 'rest'}

conditions_mytask2 = {'ev1': 'objects', \
'ev1': 'faces', \
'ev2': 'scrambled objects', \
'ev3': 'scrambled faces', \
'no_ev': 'rest'}

# loop over subjects
for ind, sub_row in subs.iterrows():
    print(sub_row.id)
    # directory where rawdata is stored. Output directory for events.tsv file
    DD = os.path.join('rootdir', 'sub-' + sub_row.id)
    # directory where feat folders are stored
    OD = os.path.join('rootdir'', 'derivatives', 'sub-' + sub_row.id)

    # loop over tasks
    for task in task_list:
        print(task)
        if task == 'mytask1':
            con_dict = conditions_mytask1
        elif task == 'mytask2':
            con_dict = conditions_mytask2

        # initialize emtpy data frame
        events_df = pd.DataFrame(columns=('onset','duration','block_type'))

        # loop over task EVs timing files
        for ev, condition in con_dict.items():
            if ev != 'no_ev':
                # derive timing file for the EV and extract values for block onset and duration
                # example timing files that are output by FEAT are provided in the folder, where this script is stored
                timing_file = os.path.join(OD, 'func', 'task', 'feats' ,task + '.feat', 'custom_timing_files', ev + '.txt')
                with open(timing_file) as f:
                    f_txt = f.readlines()
                    for line in f_txt:
                        block = str.split(line.rstrip())
                        # derive onset, duration and type of block and append to dataframe
                        events_df = events_df.append({'onset':int(block[0]) ,'duration': int(block[1]), 'block_type': condition}, ignore_index=True)

        # sort data frame
        events_df = events_df.sort_values(by='onset')
        events_df = events_df.reset_index(drop=True)
        max_row = pd.to_numeric(events_df.onset).idxmax()

        # search for undefined time segments and fill with baseline condition
        for ind, row in events_df.iterrows():
            new_row_onset = row.onset + row.duration
            if ind < max_row :
                new_row_duration = events_df['onset'][ind + 1] - new_row_onset
            else:
                new_row_duration = length_tasks[task] - new_row_onset
            events_df = events_df.append({'onset': new_row_onset, 'duration': new_row_duration, 'block_type': con_dict['no_ev']}, ignore_index=True)

        # sort data frame
        events_df = events_df.sort_values(by='onset')
        events_df = events_df.reset_index(drop=True)

        # save output
        out_file = os.path.join(DD, 'func', 'sub-' + sub_row.id + '_task-' + task + '_events.tsv')
        events_df.to_csv(out_file, sep='\t', index=False)
