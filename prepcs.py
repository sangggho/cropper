import argparse
from pathlib import Path

import cv2 as cv


def label_reader(label_file):
    # Label Data
    with open(str(label_file), 'r') as label:
        line = label.readlines()
        info = [l.strip() for l in line]

    count_info_line = len(info)
    label_info = dict()
    for i in range(count_info_line):
        split_info = info[i].split(' ')
        id = split_info[0]
        center_x_ratio = float(split_info[1])
        center_y_ratio = float(split_info[2])
        width_ratio = float(split_info[3])
        height_ratio = float(split_info[4])

        label_info.update({
            'ID': id,
            'CENTER_X_RATIO': center_x_ratio,
            'CENTER_Y_RATIO': center_y_ratio,
            'WIDTH_RATIO': width_ratio,
            'HEIGHT_RATIO': height_ratio
        })
    return label_info


def bbox_info(label_file, img_width, img_height):
    label_info = label_reader(label_file)
    cxr = label_info['CENTER_X_RATIO']
    cyr = label_info['CENTER_Y_RATIO']
    wr = label_info['WIDTH_RATIO']
    hr = label_info['HEIGHT_RATIO']

    center_x_coord = round(cxr * img_width)
    center_y_coord = round(cyr * img_height)
    bbox_width_size = round(wr * img_width)
    bbox_height_size = round(hr * img_height)

    p0 = (round(center_x_coord - bbox_width_size / 2), round(center_y_coord - bbox_height_size / 2))
    p1 = (round(center_x_coord + bbox_width_size / 2), round(center_y_coord - bbox_height_size / 2))
    p2 = (round(center_x_coord - bbox_width_size / 2), round(center_y_coord + bbox_height_size / 2))
    p3 = (round(center_x_coord + bbox_width_size / 2), round(center_y_coord + bbox_height_size / 2))

    calc_results = {
        'BBOX': (bbox_width_size, bbox_height_size),
        'POINT': (p0, p1, p2, p3)
    }
    return calc_results


def eqhist(img):
    ycrcb = cv.cvtColor(img, cv.COLOR_BGR2YCrCb)
    y, cr, cb = cv.split(ycrcb)
    y2 = cv.equalizeHist(y)
    y2crcb = cv.merge([y2, cr, cb])
    img = cv.cvtColor(y2crcb, cv.COLOR_YCrCb2BGR)
    print('equalize histogram done.')
    return img


def cropper(img, img_file_path, label_file_path, opt):
    target_name, target_size, multiple, apply_eqhist = \
        opt.target_name, opt.target_size, opt.multiple, opt.apply_eqhist

    # equalize histogram
    if apply_eqhist:
        img = eqhist(img)

    h, w, ch = img.shape

    save_dir = data_dir / opt.target_name
    save_dir.mkdir(parents=True, exist_ok=True)

    # Label data & calculated values returns
    calc_value = bbox_info(label_file_path, w, h)
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
    parser = argparse.ArgumentParser(description='Cropper Options')
    parser.add_argument('--target-name', type=str, help='target name')
    parser.add_argument('--target-size', type=int, default=512, help='target size')
    parser.add_argument('--multiple', type=int, default=1, help='value for how much overlap')
    parser.add_argument('--apply-eqhist', action='store_true', help='apply equalize histogram')
    opt = parser.parse_args()

    # Directory
    data_dir = Path.cwd() / 'data'
    if not Path.exists(data_dir):
        Path(data_dir).mkdir(parents=True, exist_ok=True)

    # File Check
    file_lists = sorted(data_dir.glob(opt.target_name + '.*'))
    img_files = []
    label_files = []

    if len(file_lists) != 2:
        fname = file_lists[0].name.split('.')[0]
        with open(f'{data_dir / fname}' + '.txt', 'w') as txt:
            txt.write('0 0.5 0.5 1 1')

    for file_path in file_lists:
        if file_path.name.endswith('.jpg') or file_path.name.endswith('.png'):
            img_files.append(str(file_path))
        if file_path.name.endswith('.txt') or file_path.name.endswith('.xml'):
            label_files.append(str(file_path))

    print('\n', img_files, label_files, '\n')

    for i, l in zip(range(len(img_files)), range(len(label_files))):
        img = cv.imread(str(img_files[i]))
        try:
            cropper(img, Path(img_files[i]), Path(label_files[l]), opt)
        except TypeError:
            assert 'Input Image Name. [--target-name]'
