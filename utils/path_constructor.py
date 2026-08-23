import os


def create_path(*args):
    return os.path.join(*args)


def path_exists(path):
    return os.path.exists(path)