import numpy as np
from nibabel import load, Nifti1Image
from os.path import expanduser, join

path = r"C:\Users\George\Desktop\brain"
img = load(r"C:\Users\George\Desktop\brain\T_R_MPRAGE_Axial_0001.img")
data = img.get_fdata()


Window(data, 'MRI')