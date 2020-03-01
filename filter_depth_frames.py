#################################################################
# utility for exporting and filtering depth frames captured with
# kinect v2 in DepthKit
# removes depthkit encoding in each frames first 3 bits
#################################################################

import numpy as np
import cv2
import os
import argparse

def filter_frames(in_path, out_path, thresh=60500):

    for file in os.listdir(in_path):
        if file.endswith(".png") and '._' not in file:

            print('filtering frame {f}'.format(f=(os.path.join(in_path, file))))

            img = cv2.imread(os.path.join(in_path, file), -1)

            img[img > thresh] = 0

            # special bit shifting equivalent operation to prepare depthkit endcoded frames
            # img = ((img % (2**13)) * 8) +  (2**15 + 2**14 + 2**13)

            # depthkit compatible, non expanded range:
            # img = (img % (2**13)) +  (2**15 + 2**14 + 2**13)

            # edge filtering
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            # kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
            # (thresh, binRed) = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
            # img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=2)
            # img = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel, iterations=2)
            img = cv2.dilate(img, kernel, iterations = 1)

            # resized = cv2.resize(img, (1280,1060), interpolation = cv2.INTER_AREA)

            cv2.imwrite(out_path + file, img.astype(np.uint16))

if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--in_path", required=True,
    	help="in path of depth frames")
    ap.add_argument("-o", "--out_path", required=True,
        help="out path of depth frames")
    ap.add_argument("-t", "--threshold", required=False,
        help="depth threshold",
        default=60500)
    args = vars(ap.parse_args())

    filter_frames(args['in_path'], args['out_path'], int(args['threshold']))
