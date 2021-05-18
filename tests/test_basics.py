import pytest
from vocab.splitter import Splitter

example_dict = {
    "key": "value",
    "key2": "value2",
    "key3": "value3",
    "int_key": 1,
    "bool_key": True,
}

example_nested_dict = {
    "key": "value",
    "key2": {
        "nested_key1": "nested_value1",
        "nested_key2": 1,
        "another_dict_key": {"hello": "world", "float": 0.2, "bool": False},
    },
}

example_nested_dict_with_list_values = {
    "key": "value",
    "nested_key": {
        "simple_key": "simple_value",
        "list_key": [0, 1, 2, 3, 4, 5, {"ps": "s"}],
    },
}


def test_construct():
    cm = Splitter(example_dict)
    assert example_dict == cm.underlying
    assert cm.kd == "."
    assert cm.ld == "*"


def test_change_delimiters():
    cm = Splitter(example_dict, keys_delimiter="-", list_delimiter="+")
    assert cm.kd == "-"
    assert cm.ld == "+"


def test_iter():
    cm = Splitter(example_dict)
    assert ("key",) in cm.keys()
    assert ("key2",) in cm.keys()
    assert ("not_exist_key",) not in cm.keys()


def test_iter_nested():
    cm = Splitter(example_nested_dict)
    assert ("key",) in cm.keys()
    assert ("key2", "nested_key1") in cm.keys()
    assert ("key2", "another_dict_key", "float") in cm.keys()
    assert ("key2",) not in cm.keys()


def test_iter_list():
    cm = Splitter(example_nested_dict_with_list_values)
    assert ("key",) in cm.keys()
    assert ("nested_key", "list_key", "*0") in cm.keys()
    assert ("nested_key", "list_key", "*1") in cm.keys()
    assert ("nested_key", "list_key", "*6", "ps") in cm.keys()

    assert "s" in cm.values()


def test_iter_list_disabled():
    cm = Splitter(example_nested_dict_with_list_values, convert_lists=False)
    assert ("key",) in cm.keys()
    assert ("nested_key", "list_key") in cm.keys()
    assert ("nested_key", "list_key", "*0") not in cm.keys()


def test_getitem():
    cm = Splitter(example_nested_dict_with_list_values)

    assert cm["key"] == "value"
    assert cm["nested_key.simple_key"] == "simple_value"
    assert cm[("nested_key", "simple_key")] == "simple_value"
    assert cm["nested_key.list_key.*2"] == 2
    assert cm[("nested_key", "list_key", "*2")] == 2

    with pytest.raises(KeyError):
        a = cm["nested_key"]

    with pytest.raises(KeyError):
        a = cm[("keyyyy",)]


def test_len():
    cm = Splitter({"test": "1", "list": [1, 2, 3]})
    assert len(cm) == 4

    cm = Splitter({"test": "1", "list": [1, 2, 3]}, convert_lists=False)
    assert len(cm) == 2


def test_keys():
    cm = Splitter(example_dict)
    assert isinstance(cm.keys(), list)
    assert all([isinstance(k, tuple) for k in cm.keys()])
    assert cm.keys()[0] == ("key",)

    cm2 = Splitter(example_nested_dict)
    assert cm2.keys() == [
        ("key",),
        ("key2", "nested_key1"),
        ("key2", "nested_key2"),
        ("key2", "another_dict_key", "hello"),
        ("key2", "another_dict_key", "float"),
        ("key2", "another_dict_key", "bool"),
    ]

    cm3 = Splitter(example_nested_dict_with_list_values)
    assert ("nested_key", "list_key", "*1") in cm3.keys()


def test_values():
    cm = Splitter(example_dict)
    assert isinstance(cm.values(), list)
    assert cm.values()[0] == "value"

    cm2 = Splitter(example_nested_dict)
    assert cm2.values() == ["value", "nested_value1", 1, "world", 0.2, False]

    cm3 = Splitter(example_nested_dict_with_list_values)
    assert cm3.values() == ["value", "simple_value", 0, 1, 2, 3, 4, 5, "s"]


def test_setitem():
    cm = Splitter(dict_={})
    cm["test"] = "test_value"

    assert ("test",) in cm.keys()
    assert "test_value" in cm.values()

    cm["test2"] = {"a": "b"}
    assert ("test2", "a") in cm.keys()
    assert "b" in cm.values()

    with pytest.raises(KeyError):
        cm["some_key"]["abc"] = 256

    cm["some_key"] = {}
    cm["some_key"]["abc"] = 256
    assert ("some_key", "abc") in cm.keys()
    assert 256 in cm.values()


def test_nested_setitem():
    cm = Splitter(dict_={})
    cm[("a", "b", "c")] = "d"

    assert ("a", "b", "c") in cm.keys()
    assert "d" in cm.values()

    cm[("a", "b", "c")] = "e"
    assert "d" not in cm.values()
    assert "e" in cm.values()

    cm[("a", "b", "x")] = "y"
    assert ("a", "b", "c") in cm.keys()
    assert ("a", "b", "x") in cm.keys()
    assert "e" in cm.values()
    assert "y" in cm.values()


def test_list_setitem():
    cm = Splitter(example_dict)
    cm["list_key"] = [0]

    assert ("list_key", "*0") in cm.keys()
    assert 0 in cm.values()

    cm["list_key.*1"] = 1

    assert ("list_key", "*1") in cm.keys()
    assert 1 in cm.values()

    assert cm.underlying["list_key"] == [0, 1]

    cm["one.two.three.*0"] = "a"
    cm["one.two.three.*1"] = "b"
    cm["one.two.three.*2"] = "c"

    assert all(["a" in cm.values(), "b" in cm.values(), "c" in cm.values()])
    assert cm["one.two.three.*2"] == "c"
    assert cm.underlying["one"]["two"]["three"] == ["a", "b", "c"]


def test_delitem():
    cm = Splitter(example_dict)
    del cm["key2"]
    assert ("key2",) not in cm.keys()
    with pytest.raises(KeyError):
        del cm["abc"]["xyz"]


def test_delitem_nested():
    cm = Splitter(example_nested_dict)

    del cm[("key2", "nested_key1")]

    assert "key2" in cm.underlying.keys()
    assert ("key2", "nested_key1") not in cm.keys()
    assert ("key2", "nested_key2") in cm.keys()

    del cm["key2.another_dict_key.hello"]
    assert ("key2", "nested_key2") in cm.keys()
    assert ("key2", "another_dict_key", "bool") in cm.keys()
    assert ("key2", "another_dict_key", "hello") not in cm.keys()
