from pathlib import Path

import cv2 as cv


def equalize_histogram(img_path: str, clahe=False, clip_limit=2.0, tile_grid_size=(8, 8)):
    # input image, convert, split channel
    img = cv.imread(img_path)
    ycc = cv.cvtColor(img, cv.COLOR_BGR2YCrCb)
    y, cr, cb = cv.split(ycc)
    print('split [y][cr][cb] channels done.')

    # create CLAHE
    init_clahe = cv.createCLAHE(clip_limit, tile_grid_size)
    y_eqh = init_clahe.apply(y) if clahe else cv.equalizeHist(y)
    print(f'CLAHE is {clahe}, channel [y] apply equalize-histogram done.')

    # merge channel
    y_eqh_cc = cv.merge([y_eqh, cr, cb])
    img = cv.cvtColor(y_eqh_cc, cv.COLOR_YCrCb2BGR)

    img_name = Path(img_path).name
    cv.imwrite(f'./data/eqh_{img_name}', img)
    print(f'merge [y_eqh][cr][cb] channels, convert [ycc] to [bgr] done. check "{img_path}".\n')
    return img


def slide_crop(img_path: str, bbox_sizes, bbox_points, size=512, overlap=1, eq_hist=False):
    # input image and if, apply equalize_histogram
    img = equalize_histogram(img_path) if eq_hist else cv.imread(img_path)
    print(f'''
    equalize-histogram option is [{eq_hist}].
    *default CLAHE option is [False].
    ''')

    # label data & calculated values returns
    bbox_width_size, bbox_height_size = bbox_sizes
    p0, p1, p2, p3 = bbox_points
    print(f'''
    label value calculate done.
    - boundary-box sizes  : width {bbox_width_size}
                            height {bbox_height_size}
    - boundary-box points : p0(left-top) {p0}
                            p1(right-top) {p1} 
                            p2(left-bottom) {p2} 
                            p3(right-bottom) {p3}
    ''')

    # feature focusing
    focused_img = img[p0[1]:p2[1], p0[0]:p1[0]]

    # processing
    if overlap > 0:
        max_x_count = int(bbox_width_size / size) * overlap
        x_offset = int((bbox_width_size - size) / max_x_count)
        x_crop_count = max_x_count + 1

        max_y_count = int(bbox_height_size / size) * overlap
        y_offset = int((bbox_height_size - size) / max_y_count)
        y_crop_count = max_y_count + 1

        img_name = Path(img_path).name
        save_dir = Path('./data') / img_name
        save_dir.mkdir(parents=True, exist_ok=True)

        for y in range(y_crop_count):
            y0 = y * y_offset
            y1 = y0 + size
            for x in range(x_crop_count):
                x0 = x * x_offset
                x1 = x0 + size
                cropped_img = focused_img[y0:y1, x0:x1]
                cv.imwrite(f'{save_dir}/{y:02d}-{x:02d}_{img_name}', cropped_img)
                print(f'check "{y:02d}-{x:02d}_{img_name}" file.')
