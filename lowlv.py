import cv2 as cv


class LowLv:
    """
    low-level image pre-processing class
    low-level computer-vision things :
    - delete image noise
    - effect of shading
    - increase definition of image
    - etc, ...
    """

    def __init__(self, img_path: str):
        self.img = cv.imread(img_path)
        self.height, self.width, self.channel = self.img.shape

    def __str__(self):
        return f'Image Shape : ({self.width}, {self.height}, {self.channel})'

    def __repr__(self):
        return self.img

    @staticmethod
    def equalize_histogram(img, clahe=False, clip_limit=2.0, tile_grid_size=(8, 8)):
        ycc = cv.cvtColor(img, cv.COLOR_BGR2YCrCb)
        y, cr, cb = cv.split(ycc)
        y_eqh = cv.equalizeHist(y)
        if clahe:
            init_clahe = cv.createCLAHE(clip_limit, tile_grid_size)
            y_eqh = init_clahe.apply(y)
        y_eqh_cc = cv.merge([y_eqh, cr, cb])
        img = cv.cvtColor(y_eqh_cc, cv.COLOR_YCrCb2BGR)
        print('equalize histogram done.')
        return img

    def cropper(self, img):
        pass

    @staticmethod
    def cropper(img, opt):
        target_name, target_size, multiple, apply_eqhist = \
            opt.target_name, opt.target_size, opt.multiple, opt.apply_eqhist

        # equalize histogram
        if apply_eqhist:
            img = eqhist(img, type='clahe')

        save_dir = data_dir / opt.target_name
        save_dir.mkdir(parents=True, exist_ok=True)

        lb = Labeler(label_file_path)
        # label data & calculated values returns
        calc_value = lb.describe_bbox(w, h)
        bbox_width_size, bbox_height_size = calc_value['BBOX']
        p0, p1, p2, p3 = calc_value['POINT']

        # feature focusing
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
