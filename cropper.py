import argparse
from pathlib import Path

import cv2 as cv


def cropper(opt):
    target_name, target_size, multiple, eqhist = \
        opt.target_name, opt.target_size, opt.multiple, opt.eqhist

    # Directory
    current_dir = Path.cwd()
    save_dir = current_dir / target_name
    save_dir.mkdir(parents=True, exist_ok=True)

    # File Check
    file_list = sorted(current_dir.glob(target_name + '.*'))
    img_file = file_list[0]
    label_file = file_list[1]

    if len(file_list) == 2:
        pass
    else:
        print('check your image file and label data.')

    # Image Data
    img = cv.imread(img_file.name)

    # equalize histogram
    if eqhist:
        ycrcb = cv.cvtColor(img, cv.COLOR_BGR2YCrCb)
        y, cr, cb = cv.split(ycrcb)
        y2 = cv.equalizeHist(y)
        y2crcb = cv.merge([y2, cr, cb])
        img = cv.cvtColor(y2crcb, cv.COLOR_YCrCb2BGR)
        print('equalize histogram done.')

    h, w, ch = img.shape

    # Label Data
    with open(label_file.name, 'r') as label:
        line = label.readlines()
        info = [l.strip() for l in line]

    count_info_line = len(info)
    for i in range(count_info_line):
        split_info = info[i].split(' ')
        id = split_info[0]
        center_x_ratio = float(split_info[1])
        center_y_ratio = float(split_info[2])
        width_ratio = float(split_info[3])
        height_ratio = float(split_info[4])

        center_x_coord = round(center_x_ratio * w)
        center_y_coord = round(center_y_ratio * h)
        bbox_width_size = round(width_ratio * w)
        bbox_height_size = round(height_ratio * h)

        p0 = (round(center_x_coord - bbox_width_size / 2), round(center_y_coord - bbox_height_size / 2))
        p1 = (round(center_x_coord + bbox_width_size / 2), round(center_y_coord - bbox_height_size / 2))
        p2 = (round(center_x_coord - bbox_width_size / 2), round(center_y_coord + bbox_height_size / 2))
        p3 = (round(center_x_coord + bbox_width_size / 2), round(center_y_coord + bbox_height_size / 2))

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

            print(f'x_offset:{x_offset}, '
                  f'y_offset:{y_offset}, '
                  f'x_crop_count:{x_crop_count}, '
                  f'y_crop_count:{y_crop_count}')

            for y in range(y_crop_count):
                y0 = y * y_offset
                y1 = y0 + target_size
                for x in range(x_crop_count):
                    x0 = x * x_offset
                    x1 = x0 + target_size
                    cropped_img = feature_img[y0:y1, x0:x1]
                    cv.imwrite(f'{save_dir}/{y:02d}-{x:02d}_{img_file.name}', cropped_img)
            print('work done.')
        else:
            print('check your multiple parameter. The multiple can not be negative.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target-name', type=str, help='target name')
    parser.add_argument('--target-size', type=int, default=512, help='target size')
    parser.add_argument('--multiple', type=int, default=1, help='value for how much overlap')
    parser.add_argument('--eqhist', action='store_true', help='apply equalize histogram')
    opt = parser.parse_args()

    try:
        cropper(opt)
    except TypeError:
        print('input image name.\n')
