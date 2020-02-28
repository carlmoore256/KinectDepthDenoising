import numpy as np
import cv2
import os
from os import walk
import argparse

def get_dframes(path):
    print('gathering depth frames')
    d_frames = []
    for root, dirs, files in os.walk(path):
        files.sort()
        for f in files:
            img = cv2.imread(os.path.join(path, f), -1)
            d_frames.append(img)
    print('found {d} depth frames'.format(d=len(d_frames)))
    return d_frames


def encode_rgb(d_frame, dims):
    # split up rgb into separate planes
    r = np.zeros((dims[0], dims[1]))
    g = np.zeros((dims[0], dims[1]))
    b = np.zeros((dims[0], dims[1]))

    # assign channels by range of 16 bit vals
    r[d_frame < 21845] = d_frame[d_frame < 21845]
    g[d_frame < 43690] = d_frame[d_frame < 43690]
    g[g < 21845] = 0
    b[d_frame >= 43690] = d_frame[d_frame >= 43690]

    # expand out range to 16 bit
    r[r>0] = r[r>0] * 3
    g[g>0] = (g[g>0] - 21845) * 3
    b[b>0] = (b[b>0] - 43690) * 3

    # divide and convert to 8 bit
    r = (r / 256).astype('uint8')
    g = (g / 256).astype('uint8')
    b = (b / 256).astype('uint8')

    return cv2.merge((r,g,b))


def merge_frames(c_frames, d_frames):

    frames = []
    dims = [c_frames[0].shape[0], c_frames[0].shape[1]]

    print('combining depth and color frames')

    for c_frame, d_frame in zip(c_frames, d_frames):

        newFrame = np.zeros((dims[0]*2, dims[1], 3))
        newFrame[:dims[0], :dims[1], :] = c_frame
        d_frame_rgb = encode_rgb(d_frame, dims)
        newFrame[dims[0]:,:dims[1], :] = d_frame_rgb
        frames.append(newFrame.astype('uint8'))

    print('frames generated')
    return frames


def generate_video(rgb_frames, depth_frames, out_path):

    frames = merge_frames(rgb_frames, depth_frames)
    dims = [ frames[0].shape[0], frames[0].shape[1] ]
    encoding = cv2.VideoWriter_fourcc(*'DIVX')

    out = cv2.VideoWriter(out_path, encoding,
                          25, (dims[1], dims[0]))

    print('writing frames to output video')

    for f in frames:
        out.write(f)
    out.release()

    print('completed writing video to {p}'.format(p=out_path))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--rgb", required=True,
    	help="path to RBG video")
    ap.add_argument("-d", "--depth", required=True,
        help="path to depth video")
    ap.add_argument("-o", "--output", required=False,
        help="output path and file extension",
        default='rgbd-merged.mp4')
    args = vars(ap.parse_args())

    generate_video(args['rgb'], args['depth'], args['output'])
