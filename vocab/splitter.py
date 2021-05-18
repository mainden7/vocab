import copy
import typing as ty
from collections.abc import MutableMapping

_AT = ty.Union[list, bool, str, float, dict, int]
_UT = ty.Union[int, float, str, bool]
_KT = ty.List[ty.Tuple[str, ...]]
_VT = ty.List[_AT]
_IT = ty.List[ty.Tuple[ty.Tuple[str, ...], _AT]]

Path = ty.Union[str, ty.Tuple[str, ...]]


def topath(func):
    def wrapper(obj, path, *args, **kwargs):
        if isinstance(path, str):
            path = tuple([key for key in path.split(obj.kd)])
        return func(obj, path, *args, **kwargs)

    return wrapper


class Splitter(MutableMapping):
    """ """

    def __init__(
        self,
        dict_: ty.Dict,
        keys_delimiter: str = ".",
        list_delimiter: str = "*",
        convert_lists: bool = True,
    ):
        super().__init__()

        if not isinstance(dict_, dict):
            raise TypeError(
                f"Only objects of type `dict` are allowed, not `{type(dict_)}`"
            )

        self.underlying = dict_
        self.kd = keys_delimiter
        self.ld = list_delimiter
        self.unconverted_types: ty.Tuple = (int, float, str, bool)
        if not convert_lists:
            self.unconverted_types += (list,)

    def __iter__(self, obj: _AT = None, path: Path = None) -> ty.Iterator:
        if obj is None:
            obj = self.underlying
        if path is None:
            path = tuple()
        # TODO: check this when obj is 0 or False and path is not None
        if isinstance(obj, self.unconverted_types) or (not obj and path):
            yield path, obj
        elif isinstance(obj, MutableMapping):
            for k, v in obj.items():
                new_path = path + (k,)
                yield from self.__iter__(v, path=new_path)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                if item is not None:
                    pos = f"{self.ld}{idx}"
                    yield from self.__iter__(item, path=path + (pos,))

    @topath
    def __setitem__(self, path: Path, value: _AT) -> None:
        if len(path) == 1:
            self.underlying[path[0]] = value
        else:
            if not path[1].startswith(self.ld):
                item = self.underlying.get(path[0], self.__class__(dict_={}))
                if isinstance(item, dict):
                    item = self.__class__(item)

                try:
                    item[path[1:]] = value
                except TypeError:
                    item = self.__class__(dict_={})
                    item[path[1:]] = value
                self.underlying[path[0]] = item.as_dict()
            else:
                self._list_insert(
                    self.underlying.setdefault(path[0], []), path[1:], value
                )

    @topath
    def __delitem__(self, path: Path) -> None:
        result = self.__class__(dict_={})
        for key, value in self:
            if key != path:
                result[key] = value
        self.underlying = result.as_dict()

    @topath
    def __getitem__(self, path: Path) -> _AT:
        value = None
        for k, v in self:
            if k == path:
                value = v
        if value is None:
            raise KeyError
        else:
            return value

    def __sub__(self, other: "Splitter") -> "Splitter":
        new_ = self.__class__(dict_={})
        for k, v in self:
            if k in other.keys() and other[k] == v:
                continue
            new_[k] = v

        return new_

    def __xor__(self, other: "Splitter") -> "Splitter":
        new_ = self.__class__(dict_={})
        for k, v in other:
            if k in self.keys() and self[k] == v:
                new_[k] = v
        return new_

    def __add__(self, other: "Splitter") -> "Splitter":
        new_ = copy.deepcopy(self)
        for k, v in other:
            if v is not None:
                new_[k] = v
        return new_

    def __len__(self) -> int:
        return len(self.keys())

    def __repr__(self) -> str:
        return str(self.underlying)

    def _list_insert(self, list_: ty.List, path: Path, value: _AT):
        pos = int(path[0][1:])
        if len(path) == 1:
            try:
                list_[pos] = value
            except IndexError:
                list_.insert(pos, value)
        else:
            empty_value = []
            if isinstance(value, self.unconverted_types):
                empty_value = ""

            if path[1].startswith(self.ld):

                try:
                    list_ = list_[pos]
                except IndexError:
                    list_.insert(pos, empty_value)
                return self._list_insert(list_, path[1:], value)
            else:
                try:
                    dict_ = list_[pos]
                    if not isinstance(dict_, self.__class__):
                        dict_ = self.__class__(dict_=dict_)
                except IndexError:
                    list_.insert(pos, self.__class__(dict_={}))
                    dict_ = list_[pos]

                dict_[path[1:]] = value
                list_[pos] = dict_.as_dict()
        return list_

    def _convert_list(self, list_):
        new_list = []
        for item in list_:
            if isinstance(item, self.__class__):
                new_list.append(item.as_dict())
            elif isinstance(item, list):
                new_list.append(self._convert_list(item))
            else:
                new_list.append(item)
        return new_list

    def as_dict(self):
        # TODO: update this method
        new_d = {}
        for k, v in self.underlying.items():
            if isinstance(v, self.unconverted_types):
                new_d[k] = v
            elif isinstance(v, self.__class__):
                new_d[k] = v.as_dict()
            elif isinstance(v, dict):
                new_d[k] = self.__class__(v).as_dict()
            elif isinstance(v, list):
                new_d[k] = self._convert_list(v)
            else:
                raise ValueError(v)
        return new_d

    def keys(self) -> _KT:
        return [k for k, _ in self]

    def values(self) -> _VT:
        return [v for _, v in self]

    def items(self):
        yield from self.__iter__()
