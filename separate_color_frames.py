import cv2
import glob
from os import listdir
from os import walk
import os

video = 'camA/RGB.mp4'
prefix = 'camA'
output_dir = 'camA/color/'

vidcap = cv2.VideoCapture(video)
success, image = vidcap.read()
count = 0

while success:
    # cv2.imwrite(output_dir + "_%d.png" % count, image)  # save frame as PNG file
    num = "{:04d}".format(count)
    cv2.imwrite('{d}{n}_{c}.png'.format(d=output_dir,n=prefix,c=num), image)  # save frame as PNG file
    success, image = vidcap.read()
    count += 1
    print('exporting frame: {c}'.format(c=count))
