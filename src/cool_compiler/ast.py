from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Optional

from .types import (
    StdType, TypeEnvironment,
    inherits, normalize, union_type, is_std_type, is_inheritable, make_inherit, type_env_of,
    _SELF_TYPE
)
from .scope import Scope


class IAST(ABCMeta):
    @abstractmethod
    def check_type(self, te: TypeEnvironment) -> str:
        raise NotImplementedError()

    @abstractmethod
    def execute(self, s: Scope):
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
        if not is_inheritable(self.inherited_type):
            raise Exception('')

        make_inherit(self.type, self.inherited_type)

        for feat in self.features:
            feat.check_type(te)

        return self.type

    def init_typecheck(self):
        if self.type == _SELF_TYPE:
            raise Exception('')

        if is_std_type(self.type):
            raise Exception('')

        te = type_env_of(self.type)
        return self.check_type(te)


class VarInitFeatureAST(IAST):
    def __init__(self, name: str, type: str, value: Optional[IAST]):
        self.name = name
        self.type = type
        self.value = value

    def check_type(self, te) -> str:
        te.set_object_type(self.name, self.type)

        if self.value != None:
            value_type = self.value.check_type(te)
            if not inherits(value_type, self.type):
                raise Exception('')

        return self.type


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
        te.set_method_type(
            self.name,
            [type for _, type in self.params],
            self.type
        )

        body_type = self.body.check_type(te)
        if not inherits(body_type, self.type):
            raise Exception('')

        return self.type


class VarMutationAST(IAST):
    def __init__(self, name: str, value: IAST):
        self.name = name
        self.value = value

    def check_type(self, te) -> str:
        var_type = te.get_object_type(self.name)
        value_type = self.value.check_type(te)

        if inherits(value_type, var_type):
            return value_type

        raise Exception('')


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
        if self.condition.check_type(te) is not StdType.Bool:
            raise Exception('Condition must be Bool type')

        true = self.then_expr.check_type(te)
        false = self.else_expr.check_type(te)
        return union_type([true, false])


class LoopExpressionAST(IAST):
    def __init__(self, condition: IAST, body: IAST):
        self.condition = condition
        self.body = body

    def check_type(self, te) -> str:
        if self.condition.check_type(te) != StdType.Bool:
            raise Exception('Loop condition must be a boolean.')
        else:
            self.body.check_type(te)
            return StdType.Object


class BlockExpressionAST(IAST):
    def __init__(self, expr_list: List[IAST]):
        self.expr_list = expr_list

    def check_type(self, te) -> str:
        last_type = None
        for exp in self.expr_list:
            last_type = exp.check_type(te)

        if last_type == None:
            return StdType.Object

        return last_type


class VarsInitAST(IAST):
    def __init__(self, var_init_list: List[Tuple[str, str, Optional[IAST]]], body: IAST):
        self.var_init_list = var_init_list
        self.body = body

    def check_type(self, te) -> str:
        self._normalize(te)

        extended_te = te.child()
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
        self.var_init_list = [(name, normalize(type, te), expr)
                              for name, type, expr in self.var_init_list]


class TypeMatchingAST(IAST):
    def __init__(self, expr: IAST, cases: List[Tuple[str, str, IAST]]):
        self.expr = expr
        self.cases = cases  # tuple is (object id, object type, expr)

    def check_type(self, te) -> str:
        self._normalize(te)

        case_types = []
        expr_types = []
        for name, type, expr in self.cases:
            clone = te.child()
            clone.set_object_type(name, type)
            expr_types.append(expr.check_type(clone))

            if not type in case_types:
                case_types.append(type)
            else:
                raise Exception(f'Only one case must have a {type} type.')

        return union_type(expr_types)

    def _normalize(self, te: TypeEnvironment):
        self.cases = [(name, normalize(type, te), expr)
                      for name, type, expr in self.cases]


class ObjectInitAST(IAST):
    def __init__(self, type: str):
        self.type = type

    def check_type(self, te) -> str:
        self._normalize(te)

        return self.type

    def _normalize(self, te: TypeEnvironment):
        self.type = normalize(self.type, te)


class UnaryOpAST(IAST):
    def __init__(self, expr: IAST):
        self.expr = expr


_VOID_VALUES = (0, "", False)


class VoidCheckingOpAST(UnaryOpAST):
    def check_type(self, _) -> str:
        return StdType.Bool

    def execute(self, s: Scope):
        value = self.expr.execute(s)
        return value in _VOID_VALUES


class NegationOpAST(UnaryOpAST):
    def check_type(self, te) -> str:
        if self.expr.check_type(te) == StdType.Int:
            return StdType.Int

        raise Exception('')

    def execute(self, s: Scope):
        return ~self.expr.execute(s)


class BooleanNegationOpAST(UnaryOpAST):
    def check_type(self, te) -> str:
        if self.expr.check_type(te) == StdType.Bool:
            return StdType.Bool

        raise Exception('')

    def execute(self, s: Scope):
        return not self.expr.execute(s)


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

    def execute(self, s: Scope):
        op = self.op[1]
        left_value = self.left.execute(s)
        right_value = self.right.execute(s)

        return op(left_value, right_value)


class ArithmeticOpAST(BinaryOpAST):
    def check_type(self, te) -> str:
        if self.left.check_type(te) is not StdType.Int or self.right.check_type(te) is not StdType.Int:
            raise TypeError(
                'The both arguments must be Int type to be valids.')

        return StdType.Int


class ComparisonOpAST(BinaryOpAST):
    def check_type(self, te) -> str:
        left_type = self.left.check_type(te)
        right_type = self.right.check_type(te)

        if self.op[0] is '=':
            if left_type == right_type:
                return StdType.Bool

            raise Exception('')

        if left_type is not StdType.Int or right_type is not StdType.Int:
            raise TypeError('Both arguments must be Int,')

        return StdType.Bool


class GroupingAST(IAST):
    def __init__(self, expr: IAST):
        self.expr = expr

    def check_type(self, te) -> str:
        return self.expr.check_type(te)

    def execute(self, s: Scope):
        return self.expr.execute(s)


_SELF = 'self'


class IdentifierAST(IAST):
    def __init__(self, name: str):
        self.name = name

    def check_type(self, te) -> str:
        if self.name == _SELF:
            return te.type

        return te.get_object_type(self.name)

    def execute(self, s: Scope):
        if self.name == _SELF:
            return s.self_value

        return s.get_var(self.name)


class LiteralAST(IAST):
    def __init__(self, value: str):
        self.value = value


class BooleanAST(LiteralAST):
    def check_type(self, _) -> str:
        return StdType.Bool

    def execute(self, _):
        return self.value == 'true'


class StringAST(LiteralAST):
    def check_type(self, _) -> str:
        return StdType.String

    def execute(self, _):
        return self.value


class IntAST(LiteralAST):
    def check_type(self, _) -> str:
        return StdType.Int

    def execute(self, _):
        return int(self.value)
