import os
import time
from datetime import datetime


def setup_path():
    if 'HQ_HOME' in os.environ:
        hq_dir = os.environ.get('HQ_HOME')
    else:
        hq_base_dir = os.path.expanduser('~')
        hq_dir = os.path.join(hq_base_dir, '.hqbot')
        os.environ["HQ_HOME"] = hq_dir

    hq_img_dir = os.path.join(hq_dir, 'imgs')

    if os.path.exists(hq_dir) is False:
        os.makedirs(hq_img_dir)
    elif os.path.exists(hq_img_dir) is False:
        os.mkdir(hq_img_dir)


def get_path():
    if 'HQ_HOME' not in os.environ:
        setup_path()
    return os.environ.get('HQ_HOME')


def get_img_name():
    base_path = get_path()

    date = datetime.now().strftime("%m_%d_%Y")
    imgs_path = os.path.join(base_path, "imgs", date)
    if os.path.exists(imgs_path) is False:
        os.mkdir(imgs_path)

    img_name = "question_{}.png".format(time.time())

    img_path = os.path.join(imgs_path, img_name)
    return img_path
