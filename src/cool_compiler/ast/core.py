from abc import ABCMeta, abstractmethod

from ..scope import Scope


class StdType:
    Bool = "Bool"
    Int = "Int"
    String = "String"
    IO = "IO"
    Object = "Object"


class IAST(ABCMeta):
    @abstractmethod
    def type(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def is_valid(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def evaluate(self, parent_scope: Scope):
        raise NotImplementedError()
