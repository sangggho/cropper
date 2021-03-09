import argparse
from pathlib import Path

import cv2 as cv

from labeler import Labeler


def eqhist(img, type=None):
    ycrcb = cv.cvtColor(img, cv.COLOR_BGR2YCrCb)
    y, cr, cb = cv.split(ycrcb)
    y2 = cv.equalizeHist(y)
    if type == 'clahe':
        clahe = cv.createCLAHE(2.0, (8, 8))
        y2 = clahe.apply(y)
    y2crcb = cv.merge([y2, cr, cb])
    img = cv.cvtColor(y2crcb, cv.COLOR_YCrCb2BGR)
    print('equalize histogram done.')
    return img


def cropper(img, img_file_path, label_file_path, opt):
    target_name, target_size, multiple, apply_eqhist = \
        opt.target_name, opt.target_size, opt.multiple, opt.apply_eqhist

    # equalize histogram
    if apply_eqhist:
        img = eqhist(img, type='clahe')

    h, w, ch = img.shape

    save_dir = data_dir / opt.target_name
    save_dir.mkdir(parents=True, exist_ok=True)

    lb = Labeler(label_file_path)
    # Label data & calculated values returns
    calc_value = lb.describe_bbox(w, h)
    bbox_width_size, bbox_height_size = calc_value['BBOX']
    p0, p1, p2, p3 = calc_value['POINT']

    # Feature Focusing
    feature_img = img[p0[1]:p2[1], p0[0]:p1[0]]

    # crop processing
    if multiple > 0:
        max_x_count = int(bbox_width_size / target_size) * multiple
        x_offset = int((bbox_width_size - target_size) / max_x_count)
        x_crop_count = max_x_count + 1

        max_y_count = int(bbox_height_size / target_size) * multiple
        y_offset = int((bbox_height_size - target_size) / max_y_count)
        y_crop_count = max_y_count + 1

        print(f'X_OFFSET:{x_offset}',
              f'Y_OFFSET:{y_offset}',
              f'X_CROP_COUNT:{x_crop_count}',
              f'Y_CROP_COUNT:{y_crop_count}')

        for y in range(y_crop_count):
            y0 = y * y_offset
            y1 = y0 + target_size
            for x in range(x_crop_count):
                x0 = x * x_offset
                x1 = x0 + target_size
                cropped_img = feature_img[y0:y1, x0:x1]
                cv.imwrite(f'{save_dir}/{y:02d}-{x:02d}_{img_file_path.name}', cropped_img)
        print('Cropped Image By Option Value.')
    else:
        print('check your multiple parameter. The multiple can not be negative.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pre-Processing Options')
    parser.add_argument('--job', type=str, help='choose your job')
    parser.add_argument('--target-name', type=str, help='target name')
    parser.add_argument('--target-size', type=int, default=512, help='target size')
    parser.add_argument('--multiple', type=int, default=1, help='value for how much overlap')
    parser.add_argument('--apply-eqhist', action='store_true', help='apply equalize histogram')
    opt = parser.parse_args()

    # Directory
    data_dir = Path.cwd() / 'data'
    if not Path.exists(data_dir):
        Path(data_dir).mkdir(parents=True, exist_ok=True)

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
                cropper(img, Path(img_files[i]), Path(label_files[l]), opt)
            except TypeError:
                assert 'Input Image Name. [--target-name]'

    elif opt.job == 'deform_checker':
        pass

    else:
        print('''
        Take Your Job that You Want. [--job JOB_NAME]
        JOB_NAME : cropper, deform_checker
        ''')
