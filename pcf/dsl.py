from __future__ import annotations
from abc import ABC, abstractmethod

from pcf.term import *


class TermBuilder(ABC):
    @abstractmethod
    def build(self) -> Term:
        raise NotImplementedError()


class PcfTypeBuilder(ABC):
    @abstractmethod
    def build(self) -> PcfType:
        raise NotImplementedError()


Named = str | Variable | BoundVariable
Termable = int | str | Term | TermBuilder
PcfTypeable = str | PcfType | PcfTypeBuilder


def as_name(t: Termable) -> str:
    if isinstance(t, str):
        return t
    elif isinstance(t, Variable) or isinstance(t, BoundVariable):
        return t.name
    elif isinstance(t, TermBuilder):
        return as_name(as_term(t))
    else:
        raise TypeError(f"termable {t} has cant be named")


def as_term(t: Termable) -> Term:
    if isinstance(t, int):
        return Number(t)
    elif isinstance(t, str):
        if len(t) == 0:
            raise ValueError("Empty string is not Termable!")
        if t[0] == "$":
            return BoundVariable(t)
        else:
            return Variable(t)
    elif isinstance(t, Term):
        return t
    elif isinstance(t, TermBuilder):
        return as_term(t.build())


def as_pcf_type(t: PcfTypeable) -> PcfType:
    if isinstance(t, PcfTypeBuilder):
        return as_pcf_type(t.build())
    elif isinstance(t, PcfType):
        return t
    elif isinstance(t, str):
        if t == "Nat":
            return Natural()
        else:
            raise ValueError("Only Natural built in type is supported.")


class ExpressionBuilder(TermBuilder):
    ex: Term

    def build(self) -> Term:
        return self.ex

    def __init__(self, t: Termable) -> None:
        self.ex = as_term(t)

    def __add__(self, rhs: Termable) -> ExpressionBuilder:
        return ExpressionBuilder(AddOp(self.ex, as_term(rhs)))

    def __sub__(self, rhs: Termable) -> ExpressionBuilder:
        return ExpressionBuilder(SubtractOp(self.ex, as_term(rhs)))

    def __mul__(self, rhs: Termable) -> ExpressionBuilder:
        return ExpressionBuilder(MultiplyOp(self.ex, as_term(rhs)))

    def __truediv__(self, rhs: Termable) -> ExpressionBuilder:
        return ExpressionBuilder(DivideOp(self.ex, as_term(rhs)))

    def __call__(self, rhs: Termable) -> ExpressionBuilder:
        return ExpressionBuilder(Application(self.ex, as_term(rhs)))


class FunBuilder(TermBuilder):
    _parameter: BoundVariable
    _body: Term | None = None

    def __init__(self, named: Termable, typed: PcfTypeable | None = None) -> None:
        self._parameter = BoundVariable(as_name(named))

    def build(self) -> Function:
        if self._body is None:
            raise ValueError("FunBuilder cant build fun with body")
        return Function(self._parameter, self._body)

    def to_(self, term: Termable) -> Function:
        self._body = as_term(term)
        return self.build()


class IfzBuilder(TermBuilder):
    _if_zero_: Term
    _then_: Term | None = None
    _else_: Term | None = None

    def __init__(self, if_zero_: Termable) -> None:
        self._if_zero_ = as_term(if_zero_)

    def build(self) -> IfZero:
        if self._then_ is None:
            raise ValueError("IfzBuilder cant build fun with then_ clause")
        if self._else_ is None:
            raise ValueError("IfzBuilder cant build fun with else_ clause")
        return IfZero(self._if_zero_, self._then_, self._else_)

    def then_(self, then_: Termable) -> IfzBuilder:
        self._then_ = as_term(then_)
        return self

    def else_(self, else_: Termable) -> IfZero:
        self._else_ = as_term(else_)
        return self.build()


class FixBuilder(TermBuilder):
    _fixed: BoundVariable
    _body: Term | None = None

    def __init__(
        self,
        named: Termable,
    ) -> None:
        self._fixed = BoundVariable(as_name(named))

    def build(self) -> Fix:
        if self._body is None:
            raise ValueError("FixBuilder cant build fun with body")
        return Fix(self._fixed, self._body)

    def in_(self, t: Termable) -> Fix:
        self._body = as_term(t)
        return self.build()


class LetBuilder(TermBuilder):
    _variable: BoundVariable
    _value: Term | None = None
    _in_: Term | None = None

    def __init__(self, named: Termable) -> None:
        self._variable = BoundVariable(as_name(named))

    def build(self) -> Let:
        if self._value is None:
            raise ValueError("LetBuilder cant build fun with value clause")
        if self._in_ is None:
            raise ValueError("LetBuilder cant build fun with in_ clause")
        return Let(self._variable, self._value, self._in_)

    def be_(self, t: Termable) -> LetBuilder:
        self._value = as_term(t)
        return self

    def in_(self, t: Termable) -> Let:
        self._in_ = as_term(t)
        return self.build()

class FunctionTypeBuilder(PcfTypeBuilder):


t = ExpressionBuilder
map = FunBuilder
ifz = IfzBuilder
fix = FixBuilder
let = LetBuilder

# fmt: off
a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z = t("a"), t("b"), t("c"), t("d"), t("e"), t("f"), t("g"), t("h"), t("i"), t("j"), t("k"), t("l"), t("m"), t("n"), t("o"), t("p"), t("q"), t("r"), t("s"), t("t"), t("u"), t("v"), t("w"), t("x"), t("y"), t("z")
# fmt: on

if __name__ == "__main__":
    print(
        map(x).to_(
            let(f)
            .be_(
                map(y).to_(y * y),
            )
            .in_((x + 1) * f(4))
        )
    )
