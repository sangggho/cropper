##
import os

import cv2 as cv
import matplotlib.pyplot as plt


##
class Cropper:
    def __init__(self, img_path: str, label_path: str, target_size=512):
        self.img_path = img_path
        self.img_name = self.img_path.split('/')[-1]
        self.label_path = label_path

        self.src_img = self._read_img()
        self.h, self.w, self.ch = self.src_img.shape

        rect_info = self.get_rect_info()
        self.xC, self.yC = rect_info['xCenter'], rect_info['yCenter']
        self.feature_height, self.feature_width = rect_info['featureHeightSize'], rect_info['featureWidthSize']
        self.p0, self.p1, self.p2, self.p3 = self._calc_rect_coord()

        self.target_size = target_size

        print(self.img_path, self.label_path, self.img_name, self.target_size)

    def _read_img(self):
        img = cv.imread(self.img_path)
        return img

    def get_yolo_label(self):
        with open(self.label_path, 'r') as line:
            split_line = line.read().split()
            label_info = {
                'id': split_line[0],
                'midX': split_line[1],
                'midY': split_line[2],
                'width': split_line[3],
                'height': split_line[4],
            }
        return label_info

    def get_rect_info(self):
        yololabel = self.get_yolo_label()
        x_center = float(yololabel['midX']) * self.w
        y_center = float(yololabel['midY']) * self.h
        width_size = float(yololabel['width']) * self.w
        height_size = float(yololabel['height']) * self.h

        rect_info = {
            'xCenter': round(x_center),
            'yCenter': round(y_center),
            'featureWidthSize': round(width_size),
            'featureHeightSize': round(height_size),
            'p0_abs': (0, 0),
            'p1_abs': (0, round(width_size)),
            'p2_abs': (0, round(height_size)),
            'p3_abs': (round(width_size), round(height_size))
        }
        return rect_info

    def _calc_rect_coord(self):
        p0 = (round(self.xC - self.feature_width / 2), round(self.yC - self.feature_height / 2))
        p1 = (round(self.xC + self.feature_width / 2), round(self.yC - self.feature_height / 2))
        p2 = (round(self.xC - self.feature_width / 2), round(self.yC + self.feature_height / 2))
        p3 = (round(self.xC + self.feature_width / 2), round(self.yC + self.feature_height / 2))
        return p0, p1, p2, p3

    def plot_img_w_point(self):
        print(self.p0, self.p1, self.p2, self.p3)

        plt.figure()
        plt.imshow(cv.cvtColor(self.src_img, cv.COLOR_BGR2RGB))
        plt.plot(self.p0[0], self.p0[1], 'r.')
        plt.plot(self.p1[0], self.p1[1], 'r.')
        plt.plot(self.p2[0], self.p2[1], 'r.')
        plt.plot(self.p3[0], self.p3[1], 'r.')
        plt.show()

    def _check_img_size(self) -> bool:
        if self.h < self.target_size or self.w < self.target_size:
            return True

    def _check_feature_size(self):
        rect_info = self.get_rect_info()
        rect_w, rect_h = rect_info['featureWidthSize'], rect_info['featureHeightSize']
        if rect_h < self.target_size or rect_w < self.target_size:
            print('consider crop full image')
        else:
            print('consider crop feature')
            return True

    def get_resize_img(self, equlize_hist=True, save=True):
        if self._check_img_size():
            resize_img = cv.resize(self.src_img, (self.target_size, self.target_size))
            print(f'{self.img_path} resized done')

            if save:
                cv.imwrite(os.path.join(os.getcwd(), 'imgs', f'resize_{self.img_name}'), resize_img)
            else:
                print('check parameters. "save", "save_path", "save_ext"')

            return resize_img

    def get_cropped_img(self, multiple=1):
        if self._check_img_size():
            _img = self.get_resize_img()
            self.img_name = f'resize_{self.img_name}'

        elif self._check_feature_size():
            _img = self.src_img[self.p0[1]:self.p2[1], self.p0[0]:self.p1[0]]

            save_dir = os.path.join(os.getcwd(), 'imgs', self.img_name.split('.')[0])
            if not os.path.isdir(save_dir):
                os.mkdir(save_dir)
            # cv.imwrite(os.path.join(os.getcwd(), f'test_{self.img_name}'), self.src_img)

            if multiple > 0:
                max_x_count = int(self.feature_width / self.target_size) * multiple
                x_offset = int((self.feature_width - self.target_size) / max_x_count)
                x_crop_count = max_x_count + 1

                max_y_count = int(self.feature_height / self.target_size) * multiple
                y_offset = int((self.feature_height - self.target_size) / max_y_count)
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
                        cv.imwrite(os.path.join(save_dir, f'{y:02d}-{x:02d}_{self.img_name}'), cropped_img)
                        print(f'{y:02d}-{x:02d}_{self.img_name} cropped')
            else:
                print('check your multiple parameter. The multiple can not be negative.')
