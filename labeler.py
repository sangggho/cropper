from pathlib import Path


class Labeler:
    def __init__(self, label_path):
        self.path = label_path
        self.lines = self._read_label()

    def _read_label(self):
        with open(str(self.path), 'r') as label:
            lines = label.readlines()
            result = [line.strip() for line in lines]
        return result

    def describe_label(self):
        cols = ['ID', 'CENTER_X_RATIO', 'CENTER_Y_RATIO', 'WIDTH_RATIO', 'HEIGHT_RATIO']
        result = dict()
        for line in self.lines:
            values = line.split(' ')
            tmp_values = []



        for idx, col in enumerate(cols):
            result.update({col: v})
        return result
