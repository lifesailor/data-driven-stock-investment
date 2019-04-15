import os


def make_folder(*paths):
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)
