from dataclasses import dataclass
from typing import ClassVar


class Term:
    pass


@dataclass
class Variable(Term):
    name: str


@dataclass
class Number(Term):
    value: int


@dataclass
class Function(Term):
    parameter: Variable
    body: Term


@dataclass
class Application(Term):
    left: Term
    right: Term


@dataclass
class BinaryOp(Term):
    op: ClassVar[str]
    left: Term
    right: Term


@dataclass
class AddOp(BinaryOp):
    op = "+"


@dataclass
class SubtractOp(BinaryOp):
    op = "-"


@dataclass
class MultiplyOp(BinaryOp):
    op = "*"


@dataclass
class DivideOp(BinaryOp):
    op = "/"


@dataclass
class IfZero(Term):
    if_zero_: Term
    then_: Term
    else_: Term


@dataclass
class Fix(Term):
    fixed: Variable
    body: Term


@dataclass
class Let(Term):
    variable: Variable
    value: Term
    in_: Term


class PcfType:
    pass


class PcfBaseType(PcfType):
    name: str


@dataclass
class Natural(PcfBaseType):
    name = "Natural"


@dataclass
class FunctionType(PcfType):
    from_: PcfType
    to_: PcfType
