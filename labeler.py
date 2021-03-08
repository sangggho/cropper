class Labeler:
    def __init__(self, label_path):
        self.path = label_path
        self.lines = self._read_label()

    def _read_label(self):
        with open(str(self.path), 'r') as label:
            lines = label.readlines()
        return [line.strip() for line in lines]

    def describe_label(self):
        columns = ['ID', 'CENTER_X_RATIO', 'CENTER_Y_RATIO', 'WIDTH_RATIO', 'HEIGHT_RATIO']
        tmp_value = []
        result = dict()
        values = [line.split(' ') for line in self.lines]
        for value_idx in range(5):
            for row_idx in range(len(values)):
                tmp_value.append(values[row_idx][value_idx])
            result.update({columns[value_idx]: tmp_value})
            tmp_value.clear()
        return result
