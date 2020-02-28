from pathlib import Path
import shutil
from os import walk
import os
import cv2
import numpy as np
# path = 'D:/Carl/DepthDenoise/curfil-master/data/training/'

label_path = 'D:/Carl/DepthDenoise/image-segmentation/data/labels_test/'

vals = []

for (dirpath, dirnames, filenames) in walk(label_path):
    for a in filenames:
        img = cv2.imread(dirpath + '/' + a,-1)
        img = img / 3000
        img = img.astype('uint8')
        cv2.imwrite(dirpath + '/' + a, img)

        # cv2.imwrite(dirpath + '/' + a, img
# vals = np.asarray(vals)
# u = np.unique(vals)
# print(u)
# vals = np.asarray(vals)
# print(np.max(vals))
        # if a.endswith('depth.png'):
        #     idx = a.find('_depth.png')
        #     shutil.copyfile(dirpath + '/' + a, depth_out + this_class + a[:idx] + '.png')
        # if a.endswith('truth.png'):
        #     idx = a.find('_ground_truth.png')
        #     shutil.copyfile(dirpath + '/' + a, label_out + this_class + a[:idx] + '.png')
