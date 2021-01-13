import os
import sys

import cv2 as cv
import matplotlib.pyplot as plt


class Cropper:
    def __init__(self, img_path: str, label_path: str, target_size=512):
        self.img_path = img_path
        self.label_path = label_path
        self.target_size = target_size

        self.img_name = img_path.split('/')[-1]

        self.img_mat, self.w, self.h, self.ch = self.read_src_img()

        self.label_info = self.show_detail_txt_label_info() \
            if label_path.split('.')[-1] == 'txt' else self.show_detail_xml_label_info()

        self.save_dir = os.path.join(os.getcwd(), 'pre-processing')
        if not os.path.isdir(self.save_dir):
            os.mkdir(self.save_dir)

    def read_src_img(self):
        img = cv.imread(self.img_path)

        if img is None:
            sys.exit("Could not read the image.")

        w = img.shape[0]
        h = img.shape[1]
        ch = img.shape[2]
        return img, w, h, ch

    def show_detail_txt_label_info(self) -> dict:
        # only support yolo label (*.txt)
        with open(self.label_path, 'r') as line:
            split_line = line.read().split()
            label_info = {
                'id': split_line[0],
                'centerXRatio': float(split_line[1]), 'centerYRatio': float(split_line[2]),
                'widthRatio': float(split_line[3]), 'heightRatio': float(split_line[4])
            }
        return label_info

    def show_detail_xml_label_info(self):
        pass

    def show_detail_bbox_info(self) -> dict:
        center_x_size = round(self.label_info['centerXRatio'] * self.w)
        center_y_size = round(self.label_info['centerYRatio'] * self.h)
        bbox_width_size = round(self.label_info['widthRatio'] * self.w)
        bbox_height_size = round(self.label_info['heightRatio'] * self.h)

        bbox_info = {
            'centerXSize': center_x_size, 'centerYSize': center_y_size,
            'bboxWidthSize': bbox_width_size, 'bboxHeightSize': bbox_height_size,
        }
        return bbox_info

    def get_bbox_coords(self, status: str) -> dict:
        # get coords from src images boundary box. you can get 2 types of coordinate.
        # first is 'absolute coords' and second is 'relative coords'.
        bbox_info = self.show_detail_bbox_info()
        cX = bbox_info['centerXSize']
        cY = bbox_info['centerYSize']
        w = bbox_info['bboxWidthSize']
        h = bbox_info['bboxHeightSize']

        coords = dict()
        if status == 'abs':
            coords = {
                'p0': (0, 0), 'p1': (0, w),
                'p2': (0, h), 'p3': (w, h)
            }
        elif status == 'relative':
            coords = {
                'p0': (round(cX - w / 2), round(cY - h / 2)),
                'p1': (round(cX + w / 2), round(cY - h / 2)),
                'p2': (round(cX - w / 2), round(cY + h / 2)),
                'p3': (round(cX + w / 2), round(cY + h / 2))
            }
        else:
            print('use "status=abs" or "status=relative".')
            assert status != 'abs' or status != 'relative', 'check your parameters name.'
        return coords

    def plot_img_with_bbox_point(self):
        coords = self.get_bbox_coords('relative')

        plt.figure()
        plt.imshow(cv.cvtColor(self.img_mat, cv.COLOR_BGR2RGB))
        plt.plot(coords['p0'][0], coords['p0'][1], 'r.')
        plt.plot(coords['p1'][0], coords['p1'][1], 'r.')
        plt.plot(coords['p2'][0], coords['p2'][1], 'r.')
        plt.plot(coords['p3'][0], coords['p3'][1], 'r.')
        plt.show()

    def _check_img_size(self):
        mod = -1
        bbox_info = self.show_detail_bbox_info()
        w, h = bbox_info['bboxWidthSize'], bbox_info['bboxHeightSize']

        if self.h < self.target_size or self.w < self.target_size:
            mod = 0
        elif w < self.target_size or h < self.target_size:
            mod = 1
        else:
            mod = 2
        return mod

    def get_resize_img(self, save=True):
        if self._check_img_size() == 0:
            print('need to resize')
            resize_img = cv.resize(self.img_mat, (self.target_size, self.target_size))
            print(f'{self.img_path} resized done')

            if save:
                cv.imwrite(os.path.join(os.getcwd(), 'imgs', f'resize_{self.img_name}'), resize_img)
            else:
                pass
            return resize_img
        else:
            print('no need to resize.')

    def get_crop_img(self, multiple=1):
        if self._check_img_size() == 0:
            _img = self.get_resize_img()
            self.img_name = f'resize_{self.img_name}'

        elif self._check_img_size() == 1:
            print('use original image.')

        elif self._check_img_size() == 2:
            print('going to crop bbox image.')

            coords = self.get_bbox_coords('relative')
            _img = self.img_mat[coords['p0'][1]:coords['p2'][1], coords['p0'][0]:coords['p0'][0]]

            _save_dir = os.path.join(self.save_dir, self.img_name.split('.')[0])
            if not os.path.isdir(_save_dir):
                os.mkdir(_save_dir)
            # cv.imwrite(os.path.join(os.getcwd(), f'test_{self.img_name}'), self.src_img)

            bbox_info = self.show_detail_bbox_info()
            bbox_w = bbox_info['bboxWidthSize']
            bbox_h = bbox_info['bboxHeightSize']
            if multiple > 0:
                max_x_count = int(bbox_w / self.target_size) * multiple
                x_offset = int((bbox_w - self.target_size) / max_x_count)
                x_crop_count = max_x_count + 1

                max_y_count = int(bbox_h / self.target_size) * multiple
                y_offset = int((bbox_h - self.target_size) / max_y_count)
                y_crop_count = max_y_count + 1

                print(f'x_offset:{x_offset}, '
                      f'y_offset:{y_offset}, '
                      f'x_crop_count:{x_crop_count}, '
                      f'y_crop_count:{y_crop_count}')

                for y in range(y_crop_count):
                    y0 = y * y_offset
                    y1 = y0 + self.target_size
                    for x in range(x_crop_count):
                        x0 = x * x_offset
                        x1 = x0 + self.target_size
                        cropped_img = _img[y0:y1, x0:x1]
                        cv.imwrite(os.path.join(_save_dir, f'{y:02d}-{x:02d}_{self.img_name}'), cropped_img)
                        print(f'{y:02d}-{x:02d}_{self.img_name} cropped')
            else:
                print('check your multiple parameter. The multiple can not be negative.')
