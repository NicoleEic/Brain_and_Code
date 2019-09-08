import numpy as np
from manual_rigid_body import manual_rigid_body

# examples:
# run default settings on example_brain
#manual_rigid_body()

# rotate around AP:
manual_rigid_body(theta = np.radians([0,90,0]), type='rotation')

# translate along LR axis:
# manual_rigid_body(translation_vec = [10,0,0], type='translation')

# translate along LR axis and rotate:
# manual_rigid_body(theta = np.radians([0,90,0]), translation_vec = [10,0,0], type='rotation_translation')
