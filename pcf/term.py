from dataclasses import dataclass
from typing import ClassVar

class Term:
    pass

@dataclass
class Variable(Term):
    name: str

@dataclass
class BoundVariable(Term):
    name: str

@dataclass
class Number(Term):
    value: int

@dataclass
class Function(Term):
    parameter: BoundVariable
    body: Term

@dataclass
class BinaryOp(Term):
    op: ClassVar[str]
    left: Term
    right: Term

@dataclass
class AddOp(BinaryOp):
    op = '+'

@dataclass
class SubtractOp(BinaryOp):
    op = '-'

@dataclass
class MultiplyOp(BinaryOp):
    op = '*'

@dataclass
class DivideOp(BinaryOp):
    op = '/'

@dataclass
class IfZero(Term):
    if_zero_: Term
    then_: Term
    else_: Term

@dataclass
class Fix(Term):
    fixed: BoundVariable
    body: Term

@dataclass
class Let(Term):
    variable: BoundVariable
    value: Term
    in_: Term

