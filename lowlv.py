from pathlib import Path

import cv2 as cv

from labeler import Labeler


def equalize_histogram(img_path: str, clahe=False, clip_limit=2.0, tile_grid_size=(8, 8)):
    img = cv.imread(img_path)
    ycc = cv.cvtColor(img, cv.COLOR_BGR2YCrCb)
    y, cr, cb = cv.split(ycc)
    init_clahe = cv.createCLAHE(clip_limit, tile_grid_size)
    y_eqh = init_clahe.apply(y) if clahe else cv.equalizeHist(y)
    y_eqh_cc = cv.merge([y_eqh, cr, cb])
    img = cv.cvtColor(y_eqh_cc, cv.COLOR_YCrCb2BGR)
    print(f'"{equalize_histogram.__name__}" work done.')
    return img


def slide_crop(img_path: str, target_size=512, overlap=1, eqhist=False, **kwargs):
    img = cv.imread(img_path)
    # if equalize_histogram
    img = equalize_histogram(img_path, clahe=True) if eqhist else cv.cvtColor(img, cv.COLOR_BGR2RGB)

    # label data & calculated values returns
    lbl = Labeler()
    bbox_width_size, bbox_height_size =
    p0, p1, p2, p3 = bbox_points

    # feature focusing
    focused_img = img[p0[1]:p2[1], p0[0]:p1[0]]

    # crop processing
    if overlap > 0:
        max_x_count = int(bbox_width_size / target_size) * overlap
        x_offset = int((bbox_width_size - target_size) / max_x_count)
        x_crop_count = max_x_count + 1

        max_y_count = int(bbox_height_size / target_size) * overlap
        y_offset = int((bbox_height_size - target_size) / max_y_count)
        y_crop_count = max_y_count + 1

        data_dir = Path.cwd() / 'data'
        img_name = Path(img_path).name
        save_dir = data_dir / img_name
        save_dir.mkdir(parents=True, exist_ok=True)

        for y in range(y_crop_count):
            y0 = y * y_offset
            y1 = y0 + target_size
            for x in range(x_crop_count):
                x0 = x * x_offset
                x1 = x0 + target_size
                cropped_img = focused_img[y0:y1, x0:x1]
                cv.imwrite(f'{save_dir}/{y:02d}-{x:02d}_{Path(img_path).name}', cropped_img)
    else:
        print('check your multiple parameter. The multiple can not be negative.')
