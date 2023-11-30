from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Optional

from .types import StdType, TypeEnvironment, inherits, normalize


class IAST(ABCMeta):
    @abstractmethod
    def check_type(self, te: TypeEnvironment) -> str:
        raise NotImplementedError()


class ClassDeclarationAST(IAST):
    def __init__(
        self,
        name: str,
        parent_name: Optional[str],
        features: List[IAST]
    ):
        self.type = name
        self.inherited_type = parent_name if parent_name != None else StdType.Object
        self.features = features

    def check_type(self, te) -> str:
        raise NotImplementedError()


class VarInitFeatureAST(IAST):
    def __init__(self, name: str, type: str, value: Optional[IAST]):
        self.name = name
        self.type = type
        self.value = value

    def check_type(self, te) -> str:
        raise NotImplementedError()


class FunctionDeclarationFeatureAST(IAST):
    def __init__(
        self,
        name: str,
        params: List[Tuple[str, str]],
        return_type: str,
        body: IAST
    ):
        self.name = name
        self.params = params
        self.type = return_type
        self.body = body

    def check_type(self, te) -> str:
        raise NotImplementedError()


class VarMutationAST(IAST):
    def __init__(self, name: str, value: IAST):
        self.name = name
        self.value = value

    def check_type(self, te) -> str:
        raise NotImplementedError()


class FunctionCallAST(IAST):
    def __init__(self, name: str, args: List[IAST], owner: Optional[IAST] = None, owner_as_type: Optional[str] = None):
        self.name = name
        self.args = args
        self.owner = owner
        self.owner_as_type = owner_as_type

    def check_type(self, te) -> str:
        raise NotImplementedError()


class ConditionalExpressionAST(IAST):
    def __init__(self, condition: IAST, then_expr: IAST, else_expr: IAST):
        self.condition = condition
        self.then_expr = then_expr
        self.else_expr = else_expr

    def check_type(self, te) -> str:
        if self.condition.check_type() is not StdType.Bool:
            raise TypeError()
        elif self.condition:
            return self.then_expr.check_type()
        else:
            return self.else_expr.check_type()


class LoopExpressionAST(IAST):
    def __init__(self, condition: IAST, body: IAST):
        self.condition = condition
        self.body = body

    def check_type(self, te) -> str:
        raise NotImplementedError()


class BlockExpressionAST(IAST):
    def __init__(self, expr_list: List[IAST]):
        self.expr_list = expr_list

    def check_type(self, te) -> str:
        raise NotImplementedError()


class VarsInitAST(IAST):
    def __init__(self, var_init_list: List[Tuple[str, str, Optional[IAST]]], body: IAST):
        self.var_init_list = var_init_list
        self.body = body

    def check_type(self, te) -> str:
        self._normalize(te)

        extended_te = te.clone()
        for name, type, value in self.var_init_list:
            # type check if init value can be assigned to
            # variable within 'te'
            if value != None:
                value_type = value.check_type(te)
                if not inherits(value_type, type):
                    raise Exception('')

            # prepare 'extended_te' to type check body expr
            extended_te.set_object_type(name, type)

        return self.body.check_type(extended_te)

    def _normalize(self, te: TypeEnvironment):
        self.var_init_list = map(
            lambda t: (t[0], normalize(t[1], te), t[2]),
            self.var_init_list
        )


class TypeMatchingAST(IAST):
    def __init__(self, expr: IAST, cases: List[Tuple[str, str, IAST]]):
        self.expr = expr
        self.cases = cases  # tuple is (object id, object type, expr)

    def check_type(self, te) -> str:
        raise NotImplementedError()


class ObjectInitAST(IAST):
    def __init__(self, type: str):
        self.type = type

    def check_type(self, te) -> str:
        raise NotImplementedError()


class UnaryOpAST(IAST):
    def __init__(self, expr: IAST):
        self.expr = expr


class VoidCheckingOpAST(UnaryOpAST):
    def check_type(self, te) -> str:
        raise NotImplementedError()


class NegationOpAST(UnaryOpAST):
    def check_type(self, te) -> str:
        raise NotImplementedError()


class BooleanNegationOpAST(UnaryOpAST):
    def check_type(self, te) -> str:
        raise NotImplementedError()


BINARY_OPERATIONS = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a // b,
    '<': lambda a, b: a < b,
    '<=': lambda a, b: a <= b,
    '=': lambda a, b: a == b,
}


class BinaryOpAST(IAST):
    def __init__(self, left: IAST, right: IAST, op: str):
        self.left = left
        self.right = right
        self.op = (op, BINARY_OPERATIONS[op])


class ArithmeticOpAST(BinaryOpAST):
    def check_type(self, te) -> str:
        raise NotImplementedError()


class ComparisonOpAST(BinaryOpAST):
    def check_type(self, te) -> str:
        raise NotImplementedError()


class GroupingAST(IAST):
    def __init__(self, expr: IAST):
        self.expr = expr

    def check_type(self, te) -> str:
        return self.expr.check_type(te)


class IdentifierAST(IAST):
    def __init__(self, name: str):
        self.name = name

    def check_type(self, te) -> str:
        return te.get_object_type(self.name)


class LiteralAST(IAST):
    def __init__(self, value: str):
        self.value = value


class BooleanAST(LiteralAST):
    def check_type(self, _) -> str:
        return StdType.Bool


class StringAST(LiteralAST):
    def check_type(self, _) -> str:
        return StdType.String


class IntAST(LiteralAST):
    def check_type(self, _) -> str:
        return StdType.Int
