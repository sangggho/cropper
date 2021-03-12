# TODO : consider using pandas

class Labeler:
    """
    read, calculate values of yolo label structure
    """

    def __init__(self, label_path: str):
        self.path = label_path
        # YOLO column mean
        self.columns = ['ID', 'CENTER_X_RATIO', 'CENTER_Y_RATIO', 'WIDTH_RATIO', 'HEIGHT_RATIO']
        self.lines = self._read()
        self.describe = self._describe()

        self.__cnt_lines = len(self.lines)

    def _read(self):
        with open(self.path, 'r') as label:
            lines = label.readlines()
            result = [line.strip() for line in lines]
        return result

    def _describe(self):
        result = dict()
        tmp_value, cpy_value = [], None
        # separate values
        split_row = [line.split(' ') for line in self.lines]
        for col_idx in range(len(self.columns)):
            for row_idx in range(len(split_row)):
                tmp_value.append(split_row[row_idx][col_idx])
                # to prevent shallow copy, re-allocate
                cpy_value = tmp_value.copy()
            result.update({self.columns[col_idx]: cpy_value})
            # all tmp_value cleared include references
            tmp_value.clear()
        return result

    def _calc_coords(self, **kwargs):
        for row_idx in range(self.__cnt_lines):
            center_x_ratio = float(self.describe[self.columns[1]][row_idx])
            center_y_ratio = float(self.describe[self.columns[2]][row_idx])
            if 'width' in kwargs.keys() and 'height' in kwargs.keys():
                center_x_coord = round(center_x_ratio * kwargs['width'])
                center_y_coord = round(center_y_ratio * kwargs['height'])
                yield center_x_coord, center_y_coord

    def _calc_sizes(self, **kwargs):
        for row_idx in range(self.__cnt_lines):
            w_ratio = float(self.describe[self.columns[3]][row_idx])
            h_ratio = float(self.describe[self.columns[4]][row_idx])
            if 'width' in kwargs.keys() and 'height' in kwargs.keys():
                bbox_w_size = round(w_ratio * kwargs['width'])
                bbox_h_size = round(h_ratio * kwargs['height'])
                yield bbox_w_size, bbox_h_size

    def _circular(self, mode: str, img_width_height: tuple):
        result = dict()
        tmp_value, cpy_value = [], None
        cnt_width_height = len(img_width_height)
        if cnt_width_height <= 2:
            w, h = img_width_height
            if mode == 'coords':
                for coords_value in self._calc_coords(width=w, height=h):
                    tmp_value.append(coords_value)
            elif mode == 'sizes':
                for sizes_value in self._calc_sizes(width=w, height=h):
                    tmp_value.append(sizes_value)
            cpy_value = tmp_value.copy()
            result.update({mode.upper(): cpy_value})
            tmp_value.clear()
            return result

    @staticmethod
    def get_points(coords: tuple, sizes: tuple):
        for x_coord, y_coord, w_size, h_size in zip(coords, sizes):
            p0 = (round(x_coord - w_size / 2), round(y_coord - h_size / 2))
            p1 = (round(x_coord + w_size / 2), round(y_coord - h_size / 2))
            p2 = (round(x_coord - w_size / 2), round(y_coord + h_size / 2))
            p3 = (round(x_coord + w_size / 2), round(y_coord + h_size / 2))
            yield p0, p1, p2, p3
