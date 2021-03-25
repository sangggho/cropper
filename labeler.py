from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


# TODO : consider using pandas

@dataclass
class YOLO:
    """
    define yolo label structure
    """
    _class_id: List[int] = field(default_factory=list)
    _center_x_ratio: List[float] = field(default_factory=list)
    _center_y_ratio: List[float] = field(default_factory=list)
    _width_ratio: List[float] = field(default_factory=list)
    _height_ratio: List[float] = field(default_factory=list)

    def bbox_coords(self, img_width: int, img_height: int) -> dict:
        coords = defaultdict(tuple)
        for idx, (x_ratio, y_ratio) in enumerate(zip(self._center_x_ratio, self._center_y_ratio)):
            x_coord = float(x_ratio) * img_width
            y_coord = float(y_ratio) * img_height
            coords[idx] = (x_coord, y_coord)
        return coords

    def bbox_sizes(self, img_width: int, img_height: int) -> dict:
        sizes = defaultdict(tuple)
        for idx, (w_ratio, h_ratio) in enumerate(zip(self._width_ratio, self._height_ratio)):
            w_size = float(w_ratio) * img_width
            h_size = float(h_ratio) * img_height
            sizes[idx] = (w_size, h_size)
        return sizes

    @staticmethod
    def bbox_points(coords: dict, sizes: dict) -> dict:
        points = defaultdict(tuple)
        for idx, ((x_coord, y_coord), (w_size, h_size)) in enumerate(zip(coords.values(), sizes.values())):
            p0 = (round(x_coord - w_size / 2), round(y_coord - h_size / 2))
            p1 = (round(x_coord + w_size / 2), round(y_coord - h_size / 2))
            p2 = (round(x_coord - w_size / 2), round(y_coord + h_size / 2))
            p3 = (round(x_coord + w_size / 2), round(y_coord + h_size / 2))
            points[idx] = (p0, p1, p2, p3)
        return points


class Labeler(YOLO):
    """
    labeler class integrates labels with different structure to make them work.
    """
    number_of_line = None

    def __init__(self, label_path, label_mode='yolo'):
        self._label_path = Path(label_path)
        self._label_name = self._label_path.name

        if label_mode == 'yolo':
            super(Labeler, self).__init__(*self.read_yolo())

    def read_yolo(self):
        with open(self._label_path, 'r') as file:
            lines = file.readlines()
            Labeler.number_of_line = len(lines)
            for row_idx, line in enumerate(lines):
                # delete '\n' and split values from blank
                clean_line = line.strip().split(' ')
                ref_line = [[value] for value in clean_line]
                if row_idx == 0:
                    result_line = ref_line.copy()
                # if more boundary-box label value then append value to ref-line
                if row_idx >= 1:
                    for value_idx, value in enumerate(clean_line):
                        result_line[value_idx].append(value)
        return result_line
