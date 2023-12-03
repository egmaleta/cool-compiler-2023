from typing import Mapping, List, Tuple, Optional
from collections import deque


class StdType:
    Bool = "Bool"
    Int = "Int"
    String = "String"
    IO = "IO"
    Object = "Object"


class TypeEnvironment:
    def __init__(self, type: str, parent: Optional['TypeEnvironment'] = None):
        self.type = type
        self._object_types: Mapping[str, str] = {}
        self._method_types: Mapping[str, Tuple[List[str], str]] = {}

        self._parent = parent

    def get_object_type(self, name: str) -> str:
        if name in self._object_types:
            return self._object_types[name]

        if self._parent != None:
            return self._parent.get_object_type(name)

        raise Exception('')

    def set_object_type(self, name: str, type: str):
        if name in self._object_types:
            raise Exception('')

        self._object_types[name] = type

    def get_method_type(self, name: str) -> Tuple[List[str], str]:
        if name in self._method_types:
            return self._method_types[name]

        if self._parent != None:
            return self._parent.get_method_type(name)

        raise Exception('')

    def set_method_type(self, name: str, param_types: List[str], return_type: str):
        if name in self._method_types:
            raise Exception('')

        self._method_types[name] = (param_types, return_type)

    def child(self):
        return TypeEnvironment(self.type, self)


_TYPE_TO_TE: Mapping[str, 'TypeEnvironment'] = {}
_TYPE_TO_PARENTTYPE: Mapping[str, str] = {}
_SELF_TYPE = 'SELF_TYPE'


def type_env_of(type: str):
    if type in _TYPE_TO_TE:
        return _TYPE_TO_TE[type]

    te = TypeEnvironment(type)
    _TYPE_TO_TE[type] = te
    return te


def make_inherit(type: str, parent_type: str):
    _TYPE_TO_PARENTTYPE[type] = parent_type


def inherits(type: str, parent_type: str):
    if parent_type == StdType.Object:
        return True

    t = type
    while t != None and t != StdType.Object:
        if t == parent_type:
            return True

        t = _TYPE_TO_PARENTTYPE[t]

    return False


def _repeated(types: List[str]):
    if len(types) == 0:
        return False

    first, *rest = types
    return all([type == first for type in rest])


def union_type(types: List[str]):
    type_set = set(types)
    if len(type_set) == 1:
        return type_set.pop()

    families = []

    for type in type_set:
        family = deque()

        t = type
        while t != None and t != StdType.Object:
            family.appendleft(t)
            t = _TYPE_TO_PARENTTYPE.get(t)

        families.append(family)

    least_type: Optional[str] = None
    for types in zip(*families):
        if _repeated(types):
            least_type = types[0]
        else:
            break

    return least_type if least_type != None else StdType.Object


def normalize(type: str, te: TypeEnvironment):
    return type if type != _SELF_TYPE else te.type


def is_std_type(type: str):
    return type == StdType.Bool\
        or type == StdType.Int\
        or type == StdType.String\
        or type == StdType.IO\
        or type == StdType.Object


def is_inheritable(type: str):
    return type != _SELF_TYPE\
        and type != StdType.Bool\
        and type != StdType.Int\
        and type != StdType.String
