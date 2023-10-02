from __future__ import annotations
from abc import ABC, abstractmethod

from pcf.term import *

class TermBuilder(ABC):
    @abstractmethod
    def term(self) -> Term:
        raise NotImplementedError()

Termable = int | str | Term | TermBuilder

def as_term(t: Termable) -> Term:
    if isinstance(t, int):
        return Number(t)
    elif isinstance(t, str):
        if len(t) == 0:
            raise ValueError('Empty string is not Termable!')
        if t[0] == '$':
            return BoundVariable(t)
        else:
            return Variable(t)
    elif isinstance(t, Term):
        return t
    elif isinstance(t, TermBuilder):
        return as_term(t.term())

class ExpressionBuilder(TermBuilder):
    ex: Term

    def term(self) -> Term:
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

class FunBuilder(TermBuilder):
    _parameter: BoundVariable
    _body: Term | None = None
    
    def __init__(self, name: str) -> None:
        self._parameter = BoundVariable(name)
    
    def term(self) -> Function:
        if self._body is None:
            raise ValueError('FunBuilder cant build fun with body')
        return Function(self._parameter, self._body)
    
    def mapsto(self, term: Termable) -> Function:
        self._body = as_term(term)
        return self.term()

class IfzBuilder(TermBuilder):
    _if_zero_: Term
    _then_: Term | None = None
    _else_: Term | None = None

    def __init__(self, if_zero_: Termable) -> None:
        self._if_zero_ = as_term(if_zero_)
    
    def term(self) -> IfZero:
        if self._then_ is None:
            raise ValueError('IfzBuilder cant build fun with then_ clause')
        if self._else_ is None:
            raise ValueError('IfzBuilder cant build fun with else_ clause')
        return IfZero(self._if_zero_, self._then_, self._else_)
    
    def then_(self, then_: Termable) -> IfzBuilder:
        self._then_ = as_term(then_)
        return self
    
    def else_(self, else_: Termable) -> IfZero:
        self._else_ = as_term(else_)
        return self.term()

class FixBuilder(TermBuilder):
    _fixed: BoundVariable
    _body: Term | None = None

    def __init__(self, name: str) -> None:
        self._fixed = BoundVariable(name)
    
    def term(self) -> Fix:
        if self._body is None:
            raise ValueError('FixBuilder cant build fun with body')
        return Fix(self._fixed, self._body)

    def in_(self, t: Termable) -> Fix:
        self._body = as_term(t)
        return self.term()

class LetBuilder(TermBuilder):
    _variable: BoundVariable
    _value: Term | None = None
    _in_: Term | None = None

    def __init__(self, name: str) -> None:
        self._variable = BoundVariable(name)
    
    def term(self) -> Let:
        if self._value is None:
            raise ValueError('LetBuilder cant build fun with value clause')
        if self._in_ is None:
            raise ValueError('LetBuilder cant build fun with in_ clause')
        return Let(self._variable, self._value, self._in_)

    def be(self, t: Termable) -> LetBuilder:
        self._value = as_term(t)
        return self

    def in_(self, t: Termable) -> Let:
        self._in_ = as_term(t)
        return self.term()


t = ExpressionBuilder
fun = FunBuilder
ifz = IfzBuilder
fix = FixBuilder
let = LetBuilder

# print(fun('x').mapsto(let('y').be(t('x') / t('x')).in_((t('x') + 1) * t('y'))))