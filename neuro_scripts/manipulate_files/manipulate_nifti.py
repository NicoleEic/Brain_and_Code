import numpy as np
import nibabel as nib
# load nifti image
img = nib.load('example_brain.nii.gz')
# get data matrix
img_data = img.get_data()
# create copy of data matrix which you can modify
new_data = img_data.copy()
# fill one slice in the middle of the first axis (i.e. the mid-saggital slice) with random values
mid_index = np.int(np.rint(new_data.shape[0]/2))
new_data[mid_index, :, :] = np.random.rand(new_data.shape[1], new_data.shape[2])
# create new image object with header information of original image
new_img = nib.Nifti1Image(new_data, img.affine, img.header)
# save file
nib.save(new_img,'example_brain_modified.nii.gz')
