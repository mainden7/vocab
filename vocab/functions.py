import os
import json
from pathlib import Path
from vocab.splitter import Splitter


def make_configs(target_dir: str, scan_dir: str):
    master_conf = Splitter(dict_={})
    for file in os.listdir(scan_dir):
        path = os.path.join(scan_dir, file)
        if os.path.isdir(path):
            continue
        ext = Path(path).suffix
        with open(path, "r") as f:
            if ext == ".json":
                conf = Splitter(dict_=json.loads(f.read()))

        if not master_conf:
            master_conf = conf
        else:
            master_conf = master_conf ^ conf

    # save master config
    with open(os.path.join(target_dir, "master.json"), "w") as mf:

        mf.write(json.dumps(master_conf.as_dict()))

    for file in os.listdir(scan_dir):
        path = os.path.join(scan_dir, file)
        if os.path.isdir(path):
            continue
        ext = Path(path).suffix

        with open(path, "r") as f:
            if ext == ".json":
                conf = Splitter(dict_=json.loads(f.read()))

        conf = conf - master_conf
        with open(os.path.join(target_dir, file), "w") as cf:
            cf.write(json.dumps(conf.as_dict()))
