import os
from vocab.functions import make_configs


def struct(args):
    directory = args.directory
    if not os.path.exists(directory):
        raise ValueError(f"Directory not found {os.path.abspath(directory)}")
    if not os.path.isdir(directory):
        raise ValueError(f"Given path {os.path.abspath(directory)} is not a valid directory")

    working_dir = os.path.join(os.path.abspath(directory), ".vocab")
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    return make_configs(working_dir, directory)
