---
layout: post
title: "Some bits about BIDS  - the Brain Imaging Data Structure format"
---

As a first blog entry I would like to talk about something which sits directly on the interface between the two themes of my blog - Brain and Code - , namely the way you organize your neuroimaging and behavioural data. The Brain Imaging Data Structure format (BIDS<sup>1</sup>, https://bids.neuroimaging.io) provides conventions about structuring and naming your raw data files, which is incredibly useful for sharing data both within teams and the global research community. But also, and this is why I chose to write about BIDS, it helped me to write much more structured, and reusable code.

The concept of structuring your dataset in a hierarchical format is intuitive to anyone, but the BIDS specification ensures that your naming conventions are coherent and comprehendible (even when you look at your data in a few years time). More importantly, an increasing number of software packages will understand your folder structure, so that you can directly plug your data into a existing analysis pipeline or data validation tools.


# The basic folder structure

```
my_study_dataset
 |
 +-- sub-01
 |  |  
 |  +-- anat
 |  |   |
 |  |   \--sub-01_T1w.nii
 |  |   \--sub-01_T1w.json
 |  |
 |  +-- func
 |      |
 |      \--sub-01_task-localizer_bold.nii
 |      \--sub-01_task-localizer_bold.json
 |      \--sub-01_task-localizer_bold_events.tsv
 |
 +-- sub-02
 |    
 +-- sub-03
 |
 +-- derivatives
 |   |
 |   +-- sub-01
 |   |   |
 |   |   + -- anat
 |   |   |
 |   |   + -- func
 |   |
 |   +-- sub-02
 |   |    
 |   +-- sub-03
 |   |
 |   +-- group
 |   |   |
 |   |   + -- anat
 |   |   |
 |   |   + -- func
 |
 +-- participants.tsv
 |
 +-- code   
```

In the example above you can see a simple tree structure for a study, where one structural scan and one functional localizer task scan was obtained in three subjects. In fact, the BIDS format can accommodate much more complex study designs with multiple sessions, different scanning modalities and different groups of subjects, but the logic always stays the same.

The study root directory (my_study_dataset) is on top of the hierarchy and each subject's raw data is stored in the level below. Note that each nifti-file is stored with its json-file, which should be retained from the dicom conversion. All derived data is stored within an extra subfolder. This separation ensures that you touch your raw data as little as possible to prevent painful accidents. BIDS does not prescribe specifications for your derived data, but I chose to maintain the same structure for different modalities (anat, func). In addition, I'm using a 'derived/group' subfolder, where I store group-level or average results, which is mirroring the subject-level folder structure and file names.

The participants.tsv file in our case might look like this:

```
id	age	sex	handedness	comments
01	34	w	rh	no comments
02	24	m	lh	no comments
03	30	m	rh	no comments
```
You can store as many columns as you want and update the overview file during data acquisition. It can be very useful to read in this file in your analysis scripts.

BIDS doesn't provide recommendations for the organization of your /code/ subfolder, but I found it helpful to use the modality names as prefixes for filenames. For example, I have files called anat_segmentation.sh, func_preprocess.sh, etc.


# Code snippets
Below I'm sharing some snippets of code with you, where I'm making use of the BIDS conventions. They helped me to optimize my workflow and might give you some inspiration.


#### Basic variable names

Most of my shell script start with the following lines, which define the core variable names:
```
rootdir=/mypath/my_study_dataset

# obtain the subject-id as input to function, or define via loop, etc.
subj=$1

# data directory where raw data is stored
DD=$rootdir/sub-$subj

# output directory, where derived data is stored
OD=$rootdir/derivatives/sub-$subj

# group-level output directory
GD=$rootdir/derivatives/group
```

#### Copy raw data

I'd recommend keeping a script to monitor how you copy your raw data from the scanner or server, because
it decreases the chance to mix up subjects' data - a severe problem, which will be very difficult to detect later. This is how I copied my files form a server, where dicom images had been automatically converted to nifti-format:

```
# my subject-id definition for this participant
subj=01

# subject-id assigned by scan operator
scan_id=030

rootdir=/mypath/my_study_dataset
DD=$rootdir/sub-$subj
OD=$rootdir/derivatives/sub-$subj

# prepare BIDS data folders for this subject
mkdir -p $DD/anat
mkdir $DD/func
mkdir -p $OD/anat
mkdir $OD/func

# copy the whole folder containing this subject's raw data
cp -r /serer_path/data_${scan_id} $DD/

# the filenames that are assigned at the scanner are highly study-specific
# anat
mv $DD/data_${scan_id}/*_t1_mpr*.json $DD/anat/sub-${subj}_T1w.json
mv $DD/data_${scan_id}/*_t1_mpr*.nii $DD/anat/sub-${subj}_T1w.nii

# func
mv $DD/data_${scan_id}/*_BOLD_*.json $DD/func/sub-${subj}_task-localizer_bold.json
mv $DD/data_${scan_id}/*_BOLD_*.nii $DD/func/sub-${subj}_task-localizer_bold.nii

# finally, the following line should be executed without error when all files have been copied successfully and the folder is empty:
rmdir $DD/data_${scan_id}
```

#### Loop over participants

In the following snippet I make use of the participants.tsv file at the top of a python script:
```
import pandas as pd
import os

rootdir='/mypath/my_study_dataset'
subs = pd.read_csv(os.path.join(rootdir, 'participants.tsv'), sep='\t', dtype={'id': str})
# exclude a subject
subs = subs[~subs['id'].isin(['03'])]

# loop over subjects
for ind, sub_row in subs.iterrows():
    OD = os.path.join(myscratch, 'LarynxRepresentation', 'derivatives', 'sub-' + sub_row.id)
    # do something.....
```

#### Convert FEAT timing files

I use FSL's<sup>2</sup> FEAT to analyse task fMRI data. The timing information about the GLM for FEAT is stored in form of one separate txt for each EV (or regressor). I wrote a script that converts these timing files to a single .tsv file, which can be stored as `*_events.tsv` file with the raw task data.
The whole script can be found in my Github repository at `https://github.com/NicoleEic/projects/blob/master/neuro_scripts/convert_timing_files/convert_timing_files.py`

# That's it!

I hope I could encourage you to make use of the BIDS format in your work! More information can be on the official website `https://bids.neuroimaging.io`. Thanks for reading this post :-)

Nicole


### References
<sup>1</sup> Gorgolewski, K. J. et al. The brain imaging data structure, a format for organizing and describing outputs of neuroimaging experiments. Scientific Data 3, 1–9 (2016).

<sup>2</sup> Jenkinson, M., Beckmann, C. F., Behrens, T. E. J., Woolrich, M. W. & Smith, S. M. FSL. NeuroImage 62, 782–790 (2012).
