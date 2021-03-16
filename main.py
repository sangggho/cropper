import argparse
from pathlib import Path
import numpy as np
import cv2 as cv

import lowlv as llv

# directory
DATA_DIR = Path.cwd() / 'data'
if not Path.exists(DATA_DIR):
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pre-Processing Options')
    parser.add_argument('--job', type=str, help='choose your job')
    parser.add_argument('--target-name', type=str, help='target name')
    parser.add_argument('--target-size', type=int, default=512, help='target size')
    parser.add_argument('--multiple', type=int, default=1, help='value for how much overlap')
    parser.add_argument('--apply-eqhist', action='store_true', help='apply equalize histogram')
    opt = parser.parse_args()

    if opt.job == 'cropper':
        # File Check
        file_lists = sorted(data_dir.glob(opt.target_name + '.*'))
        img_files = []
        label_files = []

        # Single file
        if len(file_lists) != 2:
            fname = file_lists[0].name.split('.')[0]
            with open(f'{data_dir / fname}' + '.txt', 'w') as txt:
                txt.write('0 0.5 0.5 1 1')

        # If more files...
        for file_path in file_lists:
            if file_path.name.endswith('.jpg') or file_path.name.endswith('.png'):
                img_files.append(str(file_path))
            if file_path.name.endswith('.txt') or file_path.name.endswith('.xml'):
                label_files.append(str(file_path))

        print('\n', img_files, label_files, '\n')

        # run cropper
        for i, l in zip(range(len(img_files)), range(len(label_files))):
            img = cv.imread(str(img_files[i]))
            try:
                llv.slide_crop(img, Path(img_files[i]), Path(label_files[l]), opt)
            except TypeError:
                assert 'Input Image Name. [--target-name]'

    elif opt.job == 'deform_checker':
        pass

    else:
        print(
            '''
            Take Your Job that You Want. [--job JOB_NAME]
            JOB_NAME : cropper, deform_checker
            '''
        )
