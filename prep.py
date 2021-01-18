import os

import cv2 as cv
import matplotlib.pyplot as plt


class PreProcessingImage:
    def __init__(self, img_path: str, label_path: str):
        self.img_path = img_path
        self.label_path = label_path
        self.img_name_w_ext = img_path.split('/')[-1]
        self.img_name = self.img_name_w_ext.split('.')[0]
        self.img_ext = self.img_name_w_ext.split('.')[-1]

        try:
            self.src_img = cv.imread(img_path)
            self.h, self.w, self.ch = self.src_img.shape
        except:
            print('check your image file or label file.')

    def get_label_info(self) -> dict:
        ext = self.label_path.split('.')[-1]
        if ext == 'txt':
            with open(self.label_path, 'r') as line:
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
                }
        elif ext == 'xml':
            pass
        else:
            pass
        return label_info

    def get_bbox_size_info(self) -> dict:
        label_info = self.get_label_info()
        cxr = label_info['centerXRatio']
        cyr = label_info['centerYRatio']
        wr = label_info['widthRatio']
        hr = label_info['heightRatio']

        size_info = {
            'centerX': round(cxr * self.w), 'centerY': round(cyr * self.h),
            'bboxWidthSize': round(wr * self.w), 'bboxHeightSize': round(hr * self.h)
        }
        return size_info

    def get_bbox_coords(self, status: str) -> tuple:
        """
        get coords from src images boundary box. you can get 2 types of coordinate.
        first is 'absolute coords' and second is 'relative coords'.
        """
        size_info = self.get_bbox_size_info()
        cxs = size_info['centerX']
        cys = size_info['centerY']
        bbox_ws = size_info['bboxWidthSize']
        bbox_hs = size_info['bboxHeightSize']

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

    def _check_img_size(self, target_size=512):
        if self.w < target_size or self.h < target_size:
            mod = 0
        else:
            mod = 1
        return mod

    def plot_image_with_coords(self):
        p0, p1, p2, p3 = self.get_bbox_coords('relative')
        plt.figure()
        plt.imshow(self.src_img)
        plt.plot(p0[0], p0[1], '.r')
        plt.plot(p1[0], p1[1], '.r')
        plt.plot(p2[0], p2[1], '.r')
        plt.plot(p3[0], p3[1], '.r')
        plt.show()

    def resize_image(self, target_size=512):
        mod = self._check_img_size(target_size)
        if mod == 0:
            print('mod 0, checked. resize available.')
            resize_img = cv.resize(self.src_img, (target_size, target_size))
            print(f'{self.img_path} resized done')

            img_name = self.img_path.split('/')[-1]
            target_path = os.path.join(os.getcwd(), 'prep_imgs')

            if not os.path.isdir(target_path):
                os.mkdir(target_path)

            cv.imwrite(os.path.join(target_path, f'resize_{img_name}'), resize_img)
            return resize_img
        else:
            print('no need to resize')

    def crop_image(self, target_size=512, multiple=1):
        mod = self._check_img_size(target_size)
        if mod == 1:
            print('mod 1, checked. crop available.')

            p0, p1, p2, p3 = self.get_bbox_coords('relative')
            feature_img = self.src_img[p0[1]:p2[1], p0[0]:p1[0]]

            _save_dir = os.path.join(os.getcwd(), self.img_name)
            if not os.path.isdir(_save_dir):
                os.mkdir(_save_dir)

            size_info = self.get_bbox_size_info()
            bbox_ws = size_info['bboxWidthSize']
            bbox_hs = size_info['bboxHeightSize']
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
                        cropped_img = feature_img[y0:y1, x0:x1]
                        cv.imwrite(os.path.join(_save_dir, f'{y:02d}-{x:02d}_{self.img_name_w_ext}'), cropped_img)
                        print(f'{y:02d}-{x:02d}_{self.img_name_w_ext} cropped done.')
            else:
                print('check your multiple parameter. The multiple can not be negative.')
