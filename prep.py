import os

import cv2 as cv


def check_img_and_label(src_path, name):
    """
    checking image and label file. also, return path string of image and label.
    :param src_path:
    :param name:
    :return:
    """
    if not os.path.isdir(src_path):
        print('there is no directory')
    else:
        file_list = os.listdir(src_path)
        for f in file_list:
            fname_w_ext = f.split('.')
            fname = fname_w_ext[0]
            ext = fname_w_ext[1]
            if fname == name:
                print(f)


def show_detail_label_info(img_path: str, label_path: str) -> dict:
    """
    now only support yolo label
    :param img_path:
    :param label_path: input label path './~/*.txt | *.xml'
    :return: label info dict
    """
    img = cv.imread(img_path)
    w, h, ch = img.shape

    ext = label_path.split('.')[-1]
    if ext == 'txt':
        with open(label_path, 'r') as line:
            split_line = line.read().split()
            id = split_line[0]
            cxr = float(split_line[1])
            cyr = float(split_line[2])
            wr = float(split_line[3])
            hr = float(split_line[4])

            label_info = {
                'id': id,
                'centerXRatio': cxr, 'centerYRatio': cyr,
                'widthRatio': wr, 'heightRatio': hr,
                'centerXSize': round(cxr * w), 'centerYSize': round(cyr * h),
                'bboxWidthSize': round(wr * w), 'bboxHeightSize': round(hr * h)
            }
    elif ext == 'xml':
        pass
    else:
        pass
    return label_info


def get_bbox_coords(status: str, label_info: dict) -> tuple:
    """
    get coords from src images boundary box. you can get 2 types of coordinate.
    first is 'absolute coords' and second is 'relative coords'.
    :param status: 'abs', 'relative'
    :param label_info:
    :return:
    """
    cxs = label_info['centerXSize']
    cys = label_info['centerYSize']
    bbox_ws = label_info['bboxWidthSize']
    bbox_hs = label_info['bboxHeightSize']

    p0 = p1 = p2 = p3 = -1

    if status == 'abs':
        p0 = (0, 0)
        p1 = (0, bbox_ws)
        p2 = (0, bbox_hs)
        p3 = (bbox_ws, bbox_hs)
    elif status == 'relative':
        p0 = (round(cxs - bbox_ws / 2), round(cys - bbox_hs / 2))
        p1 = (round(cxs + bbox_ws / 2), round(cys - bbox_hs / 2))
        p2 = (round(cxs - bbox_ws / 2), round(cys + bbox_hs / 2))
        p3 = (round(cxs + bbox_ws / 2), round(cys + bbox_hs / 2))
    else:
        print('use "status=abs" or "status=relative".')
        assert status != 'abs' or status != 'relative', 'check your parameters name.'
    return p0, p1, p2, p3


def check_img_size(img_path: str, target_size: int):
    img = cv.imread(img_path)
    w, h, ch = img.shape

    if w < target_size or h < target_size:
        mod = 0
    else:
        mod = 1

    return mod


def prep_resize(img_path: str, target_size=512):
    mod = check_img_size(img_path, target_size)
    if mod == 0:
        print('mod 0, checked. resize available.')
        img = cv.imread(img_path)
        resize_img = cv.resize(img, (target_size, target_size))
        print(f'{img_path} resized done')

        img_name = img_path.split('/')[-1]
        target_path = os.path.join(os.getcwd(), 'prep_imgs')

        if not os.path.isdir(target_path):
            os.mkdir(target_path)

        cv.imwrite(os.path.join(target_path, f'resize_{img_name}'), resize_img)
        return resize_img
    else:
        print('no need to resize')


def prep_slide_cropping(img_path: str, label_info: dict, target_size=512, multiple=1):
    mod = check_img_size(img_path, target_size)
    if mod == 1:
        print('mod 1, checked. crop available.')

        img = cv.imread(img_path)
        img_name = img_path.split('/')[-1]
        p0, p1, p2, p3 = get_bbox_coords('relative', label_info)
        _img = img[p0[1]:p2[1], p0[0]:p0[0]]

        _save_dir = os.path.join(os.getcwd(), 'prep_imgs', img_name.split('.')[0])
        if not os.path.isdir(_save_dir):
            os.mkdir(_save_dir)

        bbox_ws = label_info['bboxWidthSize']
        bbox_hs = label_info['bboxHeightSize']
        if multiple > 0:
            max_x_count = int(bbox_ws / target_size) * multiple
            x_offset = int((bbox_ws - target_size) / max_x_count)
            x_crop_count = max_x_count + 1

            max_y_count = int(bbox_hs / target_size) * multiple
            y_offset = int((bbox_hs - target_size) / max_y_count)
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
                    cropped_img = _img[y0:y1, x0:x1]
                    cv.imwrite(os.path.join(_save_dir, f'{y:02d}-{x:02d}_{img_name}'), cropped_img)
                    print(f'{y:02d}-{x:02d}_{img_name} cropped done.')
        else:
            print('check your multiple parameter. The multiple can not be negative.')
