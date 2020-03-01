import cv2
import numpy as np
import os
from os import walk
import json
import matplotlib.pyplot as plt
import merge_rgbd

def calibration():
    # currently hard-coded in calibration data to be parsed from json
    d_instrinsics = np.array([[ 365.278106689453, 0, 252.810501098633],
                    [0, 365.278106689453, 201.51579284668],
                    [0, 0, 1]])

    d_coeffs = np.array([0.094603031873703, -0.271095097064972, 0, 0, 0.0892143175005913])

    c_instrinsics = np.array([[ 1064.44616699219, 0, 944.81884765625],
                    [0, 1064.19055175781, 526.940124511719],
                    [0, 0, 1]])

    c_coeffs = np.array([0.0158644262701273, -0.0391600914299488, 0, 0, 0.078841358423233])

    rot_vec = np.array([-0.00188098498620093,-0.00199701404199004,0.00392582034692168])
    rot_mat = cv2.Rodrigues(np.asarray(rot_vec))
    translation_vec = np.array([ -0.05261559411883354, 1.63855190749018e-06, 0.000125980019220151]).T
    t_mat = cv2.hconcat((rot_mat[0], translation_vec))
    t_mat_real = np.vstack((t_mat, [0,0,0,1]))

    return [ c_instrinsics, c_coeffs, d_instrinsics, d_coeffs, t_mat_real ]


def load_frames(path):
    print('gathering frames')
    frames = []
    for root, dirs, files in os.walk(path):
        files.sort()
        for f in files:
            if f.endswith('.png'):
                img = cv2.imread(os.path.join(path, f), -1)
                # print('found {p}'.format(p=os.path.join(path, f)))
                frames.append(img)
    print('found {d} frames at path {p}'.format(d=len(frames), p=path))

    return frames


def undistort_frame(img, intrinsics, coeffs):
    undist = cv2.undistort(img, intrinsics, coeffs)
    return undist


def shift_depth(frame):
    frame = ((frame % (2**13)) * 8) + (2**15 + 2**14 + 2**13)
    return frame


def clean_dframes(frames):
    cleaner = cv2.rgbd.DepthCleaner_create(5, 7)
    cleaner.initialize()
    cleaned_dframes = []
    for f in frames:
        f = cleaner.apply(f)
        cleaned_dframes.append(f)
    return cleaned_dframes


def process_frames(c_path, d_path, calibration_data, clean_depth=False):
    c_frames = []
    d_frames = []

    for f in load_frames(c_path):
        undist = undistort_frame(f, calibration_data[0], calibration_data[1])
        # undist = cv2.resize(undist,(1280, 720))
        c_frames.append(undist)

    for f in load_frames(d_path):
        # shift out the first 3 bits encoded by dk
        # undist = cv2.resize(undist,(750,422))
        f = shift_depth(f)
        undist = undistort_frame(f, calibration_data[2], calibration_data[3])
        d_frames.append(undist)

    if clean_depth:
        d_frames = clean_dframes(d_frames)

    return c_frames, d_frames

@profile
def register_frames(d_frames, calibration_data, depthDilation=False, clean_depth=False):
    # load d_instrinsics
    unregisteredCameraMatrix = calibration_data[2]
    # load c_instrinsics
    registeredCameraMatrix = calibration_data[0]
    # load c_coeffs
    registeredDistCoefs = calibration_data[1]

    xform_matrix = calibration_data[4]

    registered_frames = []

    for i, frame in enumerate(d_frames):
        print('registering depth frame {a} of {j}'.format(a=i, j=len(d_frames)))
        registered = cv2.rgbd.registerDepth(unregisteredCameraMatrix,
                                            registeredCameraMatrix,
                                            registeredDistCoefs,
                                            xform_matrix,
                                            frame,
                                            (1920, 1080),
                                            depthDilation=depthDilation)
        # registered = cv2.resize(registered, (1920,1080))
        registered_frames.append(registered)

    if clean_depth:
        print('cleaning depth frames')
        registered = clean_dframes(registered_frames)

    return registered_frames

if __name__ == '__main__':
    calibration_data = calibration()
    c_frames, d_frames = process_frames('camA/color/',
                                        'camA/depth/',
                                        calibration_data,
                                        False)
    # c_frames = (c_frames[:])
    # d_frames = (d_frames[0:len(c_frames)])
    c_frames = (c_frames[:1])
    d_frames = (d_frames[:1])

    registered_dframes = register_frames(d_frames,
                                        calibration_data,
                                        False, True)

    # merge_rgbd.generate_video(c_frames, registered_dframes, 'rgbd_merged_C.mp4')
    prefix = 'camA_depth_'
    output_dir = 'camA/registered/'

    for i, f in enumerate(registered_dframes):
        num = "{:04d}".format(i)
        cv2.imwrite('{d}{n}_{c}.png'.format(d=output_dir,n=prefix,c=num), (f).astype('uint16'))
        # cv2.imwrite('camA/registered/depth_' + str(i) + '.png', (f).astype('uint16'))

    # for i, f in enumerate(c_frames):
    #     cv2.imwrite('camA/registered/color_' + str(i) + '.png', (f).astype('uint8'))
