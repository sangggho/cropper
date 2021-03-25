import argparse
from pathlib import Path
from PIL import Image

import lowlv as llv
from labeler import Labeler


def _make_require_dir():
    names = ['src', 'data']
    for name in names:
        path = Path.cwd() / name
        if not Path.exists(path):
            Path(path).mkdir(parents=True, exist_ok=True)
    return Path.cwd() / names[0], Path.cwd() / names[1]


src_dir, data_dir = _make_require_dir()


def _make_bundle_list(file_name):
    img_bundle, label_bundle = [], []
    file_lists = sorted(src_dir.glob(f'{file_name}.*'))
    for file_path in file_lists:
        if file_path.name.endswith('.jpg') or file_path.name.endswith('.png'):
            img_bundle.append(str(file_path))
        if file_path.name.endswith('.txt') or file_path.name.endswith('.xml'):
            label_bundle.append(str(file_path))
    return img_bundle, label_bundle


def _check_files(imgs: list, labels: list):
    result = False
    # check single file : no label file
    if len(labels) == 0:
        file_name = Path(imgs[0]).name.split('.')[0]
        # make 'fake' full boundary-box label value file
        with open(f'{src_dir / file_name}' + '.txt', 'w') as txt:
            txt.write('0 0.5 0.5 1 1')
            result = True
    return result


def working(opt):
    work, name, crop_size, crop_overlap, crop_eqh, clahe = \
        opt.work, opt.name, opt.c_size, opt.c_overlap, opt.c_eqh, opt.clahe

    img_paths, label_paths = _make_bundle_list(name)
    if _check_files(img_paths, label_paths):
        print(f'''
        make fake label file.
        values : [0 0.5 0.5 1 1]
        ''')
        img_paths, label_paths = _make_bundle_list(name)

    print(f'''
    {img_paths}
    {label_paths}
    ''')

    if work == 'slide-crop':
        for img, label in zip(img_paths, label_paths):
            target_img = Image.open(img)
            yolo_lb = Labeler(label)
            coords, sizes = yolo_lb.bbox_coords(*target_img.size), yolo_lb.bbox_sizes(*target_img.size)
            points = yolo_lb.bbox_points(coords, sizes)

            for i in range(len(points.keys())):
                llv.slide_crop(img_path=img,
                               bbox_sizes=sizes[i],
                               bbox_points=points[i],
                               size=crop_size,
                               overlap=crop_overlap,
                               eq_hist=crop_eqh)

    elif work == 'equalize-histogram':
        for img in img_paths:
            llv.equalize_histogram(img_path=img,
                                   clahe=clahe)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
    Pre-Processing Options
    * work list : [slide-crop], [equalize-histogram]
    * [c] is meaning [crop]
    ''')
    parser.add_argument('--work', type=str, default='slide-crop', help='choose your work, default [slide-crop].')
    parser.add_argument('--name', type=str, help='input file name you want.')
    parser.add_argument('--c-size', type=int, default=512, help='input size that you want.')
    parser.add_argument('--c-overlap', type=int, default=1, help='how many do you want to overlap.')
    parser.add_argument('--c-eqh', action='store_true', help='adjust equalize-histogram crop image.')
    parser.add_argument('--clahe', action='store_true', help='adjust CLAHE all work process.')
    opt = parser.parse_args()

    try:
        working(opt)
    except Exception as e:
        print(e)
