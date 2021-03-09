class Labeler:
    def __init__(self, label_path):
        self.path = label_path
        # YOLO column mean
        self.columns = ['ID', 'CENTER_X_RATIO', 'CENTER_Y_RATIO', 'WIDTH_RATIO', 'HEIGHT_RATIO']
        self.lines = self._read()
        self.describe = self._describe()

        self._cnt_lines = len(self.lines)

    def _read(self):
        with open(str(self.path), 'r') as label:
            lines = label.readlines()
        return [line.strip() for line in lines]

    def _describe(self):
        result = dict()
        tmp_value = []
        cpy_value = None
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

    def describe_bbox(self, img_width, img_height):
        result = dict()
        columns = ['COORD', 'SIZE']
        tmp_value = []
        cpy_value = None
        for row in range(len(self.lines)):
            center_x_ratio = float(self.describe[self.columns[1]][row])
            center_y_ratio = float(self.describe[self.columns[2]][row])
            width_ratio = float(self.describe[self.columns[3]][row])
            height_ratio = float(self.describe[self.columns[4]][row])

            center_x_coord = round(center_x_ratio * img_width)
            center_y_coord = round(center_y_ratio * img_height)
            bbox_width_size = round(width_ratio * img_width)
            bbox_height_size = round(height_ratio * img_height)

            return bbox_width_size, bbox_height_size

    def bbox_point(self):

            p0 = (round(center_x_coord - bbox_width_size / 2), round(center_y_coord - bbox_height_size / 2))
            p1 = (round(center_x_coord + bbox_width_size / 2), round(center_y_coord - bbox_height_size / 2))
            p2 = (round(center_x_coord - bbox_width_size / 2), round(center_y_coord + bbox_height_size / 2))
            p3 = (round(center_x_coord + bbox_width_size / 2), round(center_y_coord + bbox_height_size / 2))

            tmp_size.append([bbox_width_size, bbox_height_size])
            tmp_point.append([p0, p1, p2, p3])
            cpy_size = tmp_size.copy()
            cpy_point = tmp_point.copy()

            result.update({
                'BBOX_SIZE': cpy_size,
                'POINT':cpy_point
            })

            tmp_size.clear()
            tmp_point.clear()
        return result

