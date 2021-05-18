import os
import json
import tempfile
from vocab.splitter import Splitter
from vocab.functions import make_configs


def test_simple_intersection():
    with open(
        os.path.join(os.path.dirname(__file__), "files/conf1.json"), "r"
    ) as f1, open(
        os.path.join(os.path.dirname(__file__), "files/conf2.json"), "r"
    ) as f2:
        d1 = json.loads(f1.read())
        d2 = json.loads(f2.read())

    dd1 = Splitter(d1)
    dd2 = Splitter(d2)

    intersection = dd1 ^ dd2

    assert ("id",) in intersection.keys()
    assert ("runtime",) in intersection.keys()
    assert ("handlers", "*0", "urlRegex") in intersection.keys()
    assert (
        "deployment",
        "files",
        "example-resource-file1",
        "protocol",
    ) in intersection.keys()
    assert (
        "deployment",
        "files",
        "images/example-resource-file2",
        "protocol",
    ) in intersection.keys()

    assert ("threadsafe",) not in intersection.keys()
    assert ("use",) not in intersection.keys()
    assert (
        "handlers",
        "*0",
        "script",
        "scriptPath",
    ) not in intersection.keys()
    assert (
        "deployment",
        "files",
        "example-resource-file1",
        "sourceUrl",
    ) not in intersection.keys()
    assert (
        "deployment",
        "files",
        "images/example-resource-file2",
        "sourceUrl",
    ) not in intersection.keys()
    assert (
        "deployment",
        "files",
        "example-resource-file1",
        "compress",
    ) not in intersection.keys()
    assert (
        "deployment",
        "files",
        "images/example-resource-file2",
        "compress",
    ) not in intersection.keys()


def test_subtract():
    with open(
        os.path.join(os.path.dirname(__file__), "files/conf1.json"), "r"
    ) as f1, open(
        os.path.join(os.path.dirname(__file__), "files/conf2.json"), "r"
    ) as f2:
        d1 = json.loads(f1.read())
        d2 = json.loads(f2.read())

    dd1 = Splitter(d1)
    dd2 = Splitter(d2)

    result = dd1 - dd2
    assert ("threadsafe",) in result.keys()
    assert (
        "deployment",
        "files",
        "example-resource-file1",
        "sourceUrl",
    ) in result.keys()

    assert ("id",) not in result.keys()
    assert ("runtime",) not in result.keys()
    assert ("handlers", "*0", "urlRegex") not in result.keys()
    assert (
        "deployment",
        "files",
        "example-resource-file1",
        "protocol",
    ) not in result.keys()
    assert (
        "deployment",
        "files",
        "images/example-resource-file2",
        "protocol",
    ) not in result.keys()


def test_simple_add():
    d1 = Splitter(dict_={"a": "b"})
    d2 = Splitter(dict_={"c": "d"})

    result = d1 + d2

    assert ("a",) in result.keys()
    assert ("c",) in result.keys()
    assert "b" in result.values()
    assert "d" in result.values()


def test_nested_add():
    with open(
        os.path.join(os.path.dirname(__file__), "files/conf1.json"), "r"
    ) as f1:
        d1 = json.loads(f1.read())

    dd1 = Splitter(d1)
    dd2 = Splitter(
        dict_={
            "deployment": {
                "files": {"example-resource-file1": {"new_key": "new_value"}}
            },
            "x": "y",
        }
    )

    result = dd1 + dd2
    assert ("x",) in result.keys()
    assert "y" in result.values()
    assert (
        "deployment",
        "files",
        "example-resource-file1",
        "sourceUrl",
    ) in result.keys()
    assert (
        "deployment",
        "files",
        "example-resource-file1",
        "new_key",
    ) in result.keys()
    assert "new_value" in result.values()


def test_list_add():
    with open(
        os.path.join(os.path.dirname(__file__), "files/conf1.json"), "r"
    ) as f1:
        d1 = json.loads(f1.read())

    dd1 = Splitter(d1)
    dd2 = Splitter(
        dict_={"x": "y", "handlers": [None, {"urlRegex": "//[.*]"}]}
    )

    result = dd1 + dd2

    assert ("x",) in result.keys()
    assert "y" in result.values()
    assert ("handlers", "*0", "urlRegex") in result.keys()
    assert ("handlers", "*1", "urlRegex") in result.keys()
    assert "/.*" in result.values()
    assert "//[.*]" in result.values()

    assert result["handlers.*0.urlRegex"] == "/.*"
    assert result["handlers.*1.urlRegex"] == "//[.*]"


def test_real_duty():
    initial_configs_dir = os.path.join(os.path.dirname(__file__), "files")
    with tempfile.TemporaryDirectory(
        dir=os.path.join(os.path.dirname(__file__), "files")
    ) as temp:
        make_configs(temp, initial_configs_dir)

        with open(os.path.join(temp, "master.json")) as mf, open(
            os.path.join(temp, "conf1.json")
        ) as b1f, open(os.path.join(temp, "conf2.json")) as b2f, open(
            os.path.join(initial_configs_dir, "conf1.json")
        ) as ib1, open(
            os.path.join(initial_configs_dir, "conf2.json")
        ) as ib2:
            mc = json.loads(mf.read())
            b1 = json.loads(b1f.read())
            b2 = json.loads(b2f.read())

            ib1 = json.loads(ib1.read())
            ib2 = json.loads(ib2.read())

        restored1 = Splitter(mc) + Splitter(b1)
        restored1 = restored1.as_dict()

        restored2 = Splitter(mc) + Splitter(b2)
        restored2 = restored2.as_dict()

        assert all([ib1[k] == restored1[k] for k in restored1.keys()])
        assert all([ib2[k] == restored2[k] for k in restored2.keys()])


def test_real_duty2():
    initial_configs_dir = os.path.join(
        os.path.dirname(__file__), "files", "configs"
    )
    with tempfile.TemporaryDirectory(
        dir=os.path.join(os.path.dirname(__file__), "files")
    ) as temp:
        make_configs(temp, initial_configs_dir)

        with open(os.path.join(temp, "master.json")) as mf, open(
            os.path.join(temp, "big1.json")
        ) as b1f, open(os.path.join(temp, "big2.json")) as b2f, open(
            os.path.join(initial_configs_dir, "big1.json")
        ) as ib1, open(
            os.path.join(initial_configs_dir, "big2.json")
        ) as ib2:
            mc = json.loads(mf.read())
            b1 = json.loads(b1f.read())
            b2 = json.loads(b2f.read())

            ib1 = json.loads(ib1.read())
            ib2 = json.loads(ib2.read())

        restored1 = Splitter(mc) + Splitter(b1)
        restored1 = restored1.as_dict()

        restored2 = Splitter(mc) + Splitter(b2)
        restored2 = restored2.as_dict()

        assert all([ib1[k] == restored1[k] for k in restored1.keys()])
        assert all([ib2[k] == restored2[k] for k in restored2.keys()])
