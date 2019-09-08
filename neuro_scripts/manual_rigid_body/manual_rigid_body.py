import numpy as np
import nibabel as nib
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')
from my_functions.matrix_stuff import *

def manual_rigid_body(fname = 'example_brain.nii.gz',
                     outmat = 'transformation.mat',
                     outimg = 'example_brain_transformed.nii.gz',
                     theta = np.radians([0,0,0]),
                     translation_vec = [0,0,0],
                     type = 'rotation',
                     flip_coordinates = [True, False, False]):

    """
    Function to perform a rigid body transformation based on manually determined parameters.

    Args:
        - fname (str): filepath to input nifti image (.nii.gz)
        - outmat (str): filepath of output 4x4 transformation matrix (.mat)
        - outimg (str): filepath of transformed output image (.nii.gz)
        - theta (np.array): vector of rotation angles in x,y,z dimension (in radians)
        - translation_vec (np.array): vector for translation in x,y,z (in image coordinates)
        - type (str): can be 'rotation' or 'translation' or 'rotation_translation'
        - flip_coordinates (boolean vector): indicates for which axis the sign of the offset needs to be flipped

    Returns:
        - M (np.array): output 4x4 transformation matrix
        - M is written to outmat
        - the output image (outimg) is written out

    Note on flip_coordinates:
        Voxel coordinates in the image are expected to increase in the following directions
        (it's similar to determining the reorient-command):
        - first dimension: left -> right
        - second dimension: posterir -> anterior
        - third dimension: inferior -> superior

        if they go the other way, change input variable accordingly, e.g.:
        flip_coordinates = [True, False, False]
    """

    # get sform from image to determine offset of coordinate-system
    img = nib.load(fname)
    aff = img.get_affine()
    offset = aff[0:3,3]

    # which type of manipulation is requested
    if type == 'rotation':
        print('do rotation only')
        M = rotation(theta, offset, flip_coordinates)
    elif type == 'translation':
        print('do translation only')
        M = vector_to_translation_matrix(translation_vec)
    elif type == 'rotation_translation':
        print('do combined rotation and translation')
        M = rotation_translation(theta, translation_vec, offset, flip_coordinates)

    # save output matrix
    print('output matrix: ', M)
    print('save in: ', outmat)
    save_matrix4x4(M, outmat)

    # apply transformation to input image
    applywarp_command = "applywarp -i " + fname + " -r " + fname + " --premat=" + outmat + " --interp=nn -o " + outimg
    print('run flirt: ', applywarp_command)
    os.system(applywarp_command)

    return M
