#################################################################
# utility for exporting and filtering depth frames captured with
# kinect v2 in DepthKit
# removes depthkit encoding in each frames first 3 bits
#################################################################

import numpy as np
import cv2
import os
from os import walk
import argparse

def filter_frames(in_path_color, in_path_depth, out_path, thresh=60500):
    color_frames = []

    for root, dirs, files in os.walk(in_path_color):
        files.sort()
        for f in files:
            if f.endswith(".png") and '._' not in f:
                color_frames.append(os.path.join(in_path_color, f))

    idx = 0
    for root, dirs, files in os.walk(in_path_depth):
        files.sort()
        for f in files:
            if f.endswith(".png") and '._' not in f:

                print('filtering frame {f}'.format(f=(os.path.join(in_path_depth, f))))

                color = cv2.imread(color_frames[idx], -1)
                depth = cv2.imread(os.path.join(in_path_depth, f), -1)

                depth_temp[depth==0] = 1
                inpaint_mask = np.zeros(depth.shape, dtype='uint8')
                inpaint_mask[depth == 0] = 255

                edges = cv2.Canny(color,100,200)

                # img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=2)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                edges = cv2.dilate(edges, kernel, iterations = 1)


                inpaint_mask[depth == 0] = 255
                inpaint_mask[:,:200] = 0
                # inpaint_mask[:,600:] = 0
                inpaint_mask[800:,:] = 0
                inpaint_mask[:300,:] = 0
                painted = cv2.inpaint(depth,inpaint_mask,3,cv2.INPAINT_TELEA)
                # mask the frame at edges
                # painted[edges>0] = 65535


                # edge filtering
                # kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
                # (thresh, binRed) = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)

                # img = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel, iterations=2)

                # resized = cv2.resize(img, (1280,1060), interpolation = cv2.INTER_AREA)

                cv2.imwrite(out_path + f, painted.astype(np.uint16))
                # cv2.imwrite(out_path + f, inpaint_mask.astype('uint8'))
                idx += 1

                break

if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--in_path_color", required=True,
    	help="in path of color frames")
    ap.add_argument("-d", "--in_path_depth", required=True,
    	help="in path of depth frames")
    ap.add_argument("-o", "--out_path", required=True,
        help="out path of depth frames")
    ap.add_argument("-t", "--threshold", required=False,
        help="depth threshold",
        default=60500)
    args = vars(ap.parse_args())

    filter_frames(args['in_path_color'], args['in_path_depth'], args['out_path'], int(args['threshold']))
