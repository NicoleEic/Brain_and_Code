import numpy as np
import math
import nibabel as nib
import os

# read in a 4x4 matrix from ascii format and convert to np.array
def read_matrix4x4(fname):
    M = np.array(map(float,open(fname, 'r').read().split())).reshape(4,4)

# save output 4x4 matrix in ascii format
def save_matrix4x4(M, fname):
    np.savetxt(fname, M, fmt='%10.5f')

def convert_rotation_matrix_3x3_to_4x4(R3):
    R4 = np.vstack((R3,[0,0,0]))
    R4 = np.hstack((R4, np.array([0,0,0,1]).reshape(-1,1)))
    return R4

# Checks if a matrix is a valid rotation matrix, returns boolean
def check_is_rotation_matrix(R):
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype = R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-4

# extracts the rotation (3x3) and translation component (3,1) from a 4x4 matrix
def split_matrix_rotation_translation(M):
    R3 = M[0:3,0:3]
    translation_vec = M[0:3,3]
    return(R3, translation_vec)

# first translate offset from sform, then rotatate, then translate back
def rotation(theta, offset, flip_coordinates):
    myvec = offset[:]
    myvec[flip_coordinates] = -myvec[flip_coordinates]
    R = angles_to_rotation_matrix(theta)
    R = convert_rotation_matrix_3x3_to_4x4(R)
    T = vector_to_translation_matrix(myvec)
    M = np.dot(np.linalg.inv(T), np.dot(R,T))
    return(M)

# Combine rotation and translation
def rotation_translation(theta, translation_vec, offset, flip_coordinates):
    R = rotation(theta, offset, flip_coordinates)
    T = vector_to_translation_matrix(translation_vec)
    C = np.dot(T,R)
    return C

# convert vector of angles to a 3x3 rotation matrix
def angles_to_rotation_matrix(theta):
    R_x = np.array([[1, 0, 0],
                 [0, math.cos(theta[0]), -math.sin(theta[0]) ],
                 [0, math.sin(theta[0]), math.cos(theta[0])  ]])
    R_y = np.array([[math.cos(theta[1]), 0, math.sin(theta[1])],
                 [0, 1, 0],
                 [-math.sin(theta[1]), 0, math.cos(theta[1])]])
    R_z = np.array([[math.cos(theta[2]), -math.sin(theta[2]), 0],
                 [math.sin(theta[2]), math.cos(theta[2]), 0],
                 [0, 0, 1]])
    R = np.dot(R_z, np.dot( R_y, R_x ))
    return R

# Transforms rotation matrix to a vector of angles
def rotation_matrix_to_angles(R):
    assert(check_is_rotation_matrix(R))
    is_symmetric = math.sqrt(R[0,0] * R[0,0] + R[1,0] * R[1,0])
    is_singular = is_symmetric < 1e-4

    if not is_singular:
        x = math.atan2(R[2,1], R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else:
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0

    theta = np.array([x, y, z])
    return theta

# generate a 4x4 homogenous translation matrix as np.array from a 3x1 vector
def vector_to_translation_matrix(translation_vec):
    T = np.array([[1, 0, 0, translation_vec[0]],
                  [0, 1, 0, translation_vec[1]],
                  [0, 0, 1, translation_vec[2]],
                  [0, 0, 0, 1]])
    return T

# get translation vector from a 4x4 homogeneous matrix
def translation_matrix_to_vector(T):
    translation_vec = M[0:3,3]
    return translation_vec
