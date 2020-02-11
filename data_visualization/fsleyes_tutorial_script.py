import os
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import fsleyes.main as main
from fsl.data.image import Image
from fsleyes.views.orthopanel import OrthoPanel
import fsl

# -------
# Change this variable:
subject_group = 'control'
# -------

# launch frames
overlayList, displayCtx, frame = main.embed()
frame.addViewPanel(OrthoPanel)
frame.Show()

# folder where data is stored
mydir = os.path.join('myPath', 'tutorial', 'data')

# filenames
df = pd.DataFrame(columns=['subject_group', 'structural', 'CST', 'MDLF'])
df.loc[len(df)] = ['control', 'structural', 'cst', 'mdlf']
df.loc[len(df)] = ['patient-group1', 'structural', 'cst', 'mdlf']
df.loc[len(df)] = ['patient-group2', 'structural', 'cst', 'mdlf']

# some settings:

# colour for the two tracts
my_colours = np.array([[0.  , 0.6 , 1.  ], # blue
                       [1.  , 0.33, 0.68]]) # pink

# display range for thresholding the tracts
display_range = (0.2, 1)

# make sure all previous overlays are removed
overlayList.clear()

# load structural
structural_fname = f'{df[df.subject_group == subject_group].structural.values[0]}.nii.gz'
load(os.path.join(os.sep, mydir, structural_fname))

# load tractograms

# loop over hemispheres
for hemi in ['l', 'r']:
    for i_t, tract in enumerate(['CST', 'MDLF']):
        tract_fname = os.path.join(os.sep, mydir,
                                   f'{df[df.subject_group == subject_group][tract].values[0]}_{hemi}.nii.gz')
        load(os.path.join(os.sep, mydir, tract_fname))

        # set display range and clipping range
        displayCtx.getOpts(overlayList[-1]).clippingRange = display_range
        displayCtx.getOpts(overlayList[-1]).displayRange = display_range

        # set colour map specific for tract type
        # use a colour map where luminance linearly increases from black to white
        displayCtx.getOpts(overlayList[-1]).cmap = LinearSegmentedColormap.from_list('mycmap',
                                                                                     ['black', my_colours[i_t],
                                                                                      'white'])
        # determine max voxel for MDLF tractogram in left hemisphere
        if (hemi == 'l') & (tract == 'MDLF'):
            max_voxel = np.unravel_index(np.argmax(overlayList[-1].data, axis=None), overlayList[-1].data.shape)

# place cross hair on maximal voxel for MDLF_L
displayCtx = frame.viewPanels[0].displayCtx
displayCtx.location = displayCtx.getOpts(overlayList[-1]).transformCoords(max_voxel, 'voxel', 'display')

# import a custom atlas
fsl.data.atlases.addAtlas('/myPath/tutorial/myatlas.xml')