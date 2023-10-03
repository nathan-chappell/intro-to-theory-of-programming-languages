from __future__ import annotations

import operator as OP

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from itertools import chain
from typing import TYPE_CHECKING, get_args

from pcf.dsl import TermBuilder, Termable, as_term
from pcf.term import *
from pcf.term import Term


@dataclass
class Declaration:
    bound_variable: Variable
    term: Term


@dataclass
class Context(Mapping[Termable, Term]):
    declarations: list[Declaration] = field(default_factory=list)
    parent: Context | None = None

    def push(self, *declarations: Declaration) -> Context:
        return Context(list(declarations), self)

    def __getitem__(self, key: Termable) -> Term:
        key_term = as_term(key)
        if not isinstance(key_term, Variable):
            raise TypeError(f"Context only accepts Variable keys: {key}")
        for declaration in self.declarations:
            if declaration.bound_variable.name == key_term.name:
                return declaration.term
        if self.parent is None:
            raise KeyError(key)
        else:
            return self.parent[key]

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, (get_args(Termable))):
            raise TypeError(f"Context only accepts Variable keys: {key}")
        if TYPE_CHECKING:
            assert isinstance(key, Termable)
        try:
            _ = self[key]
        except KeyError:
            return False
        return True

    def __iter__(self) -> Iterator[Termable]:
        self_iter = (d.bound_variable for d in self.declarations)
        if self.parent is None:
            return self_iter
        else:
            return chain(self_iter, iter(self.parent))

    def __len__(self) -> int:
        self_len = len(self.declarations)
        if self.parent is None:
            return self_len
        else:
            return self_len + len(self.parent)


def interpret(term: Term | TermBuilder, context: Context = Context()) -> int | Term:
    if isinstance(term, TermBuilder):
        return interpret(term.build(), context)
    match (term):
        case Variable(name=var_name):
            return interpret(context[var_name])

        case Number(value=num_val):
            return num_val

        case Application(left=Function(parameter=fn_param, body=fn_body), right=fn_arg):
            return interpret(fn_body, context.push(Declaration(fn_param, fn_arg)))

        case Application(left=fn_term, right=fn_arg):
            fn = interpret(fn_term, context)
            if isinstance(fn, Function):
                return interpret(Application(fn, fn_arg), context)
            else:
                return Application(as_term(fn), fn_arg)

        case BinaryOp(op=_op, left=add_l, right=add_r):
            _binop_l = interpret(add_l, context)
            _binop_r = interpret(add_r, context)
            if isinstance(_binop_l, int) and isinstance(_binop_r, int):
                operator = {
                    "+": OP.add,
                    "-": OP.sub,
                    "*": OP.mul,
                    "/": OP.truediv,
                }[_op]
                return operator(_binop_l, _binop_r)
            else:
                cls = {
                    "+": AddOp,
                    "-": SubtractOp,
                    "*": MultiplyOp,
                    "/": DivideOp,
                }[_op]
                return cls(left=as_term(_binop_l), right=as_term(_binop_r))

        case IfZero(if_zero_=if_zero_, then_=then_, else_=else_):
            _if_zero = interpret(if_zero_, context)
            if isinstance(_if_zero, int):
                if _if_zero == 0:
                    return interpret(then_, context)
                else:
                    return interpret(else_, context)
            else:
                return IfZero(as_term(_if_zero), then_, else_)

        case _:
            return term


if __name__ == "__main__":
    from pcf.dsl import *

    _term = map("x").with_body(map("y").to_(x + y))(3)(4)
    print(_term.build())
    print(interpret(_term))
