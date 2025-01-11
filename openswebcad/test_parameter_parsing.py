from typing import Annotated, Literal

import pytest

from openswebcad.plugin import get_parameters as p, InvalidParameterAnnotation as Error
from openswebcad.parameters import ChoiceParameter, IntParameter, FloatParameter
from openswebcad import Range, Help

# choice
def test_choice_simple():
    def f(a: Literal["x", "y"]): pass

    assert p(f) == [ChoiceParameter(name="a", choices=["x", "y"], helptext="")]

def test_choice_help():
    def f(a: Annotated[Literal["x", "y"], Help("bla")]): pass

    assert p(f) == [ChoiceParameter(name="a", choices=["x", "y"], helptext="bla")]

# int
def test_int_simple():
    def f(a: Annotated[int, Range(1, 3)]): pass

    assert p(f) == [IntParameter(name="a", min_value=1, max_value=3, helptext="")]


def test_int_help():
    def f(a: Annotated[int, Range(1, 3), Help("bla")]): pass

    assert p(f) == [IntParameter(name="a", min_value=1, max_value=3, helptext="bla")]

def test_int_norange():
    def f(a: int): pass

    with pytest.raises(Error):
        p(f)

def test_int_help_norange():
    def f(a: Annotated[int, Help("bla")]): pass

    with pytest.raises(Error):
        p(f)

# float
def test_float_simple():
    def f(a: Annotated[float, Range(1.0, 3.0)]): pass

    assert p(f) == [FloatParameter(name="a", min_value=1, max_value=3, helptext="")]


def test_float_help():
    def f(a: Annotated[float, Range(1.0, 3.0), Help("bla")]): pass

    assert p(f) == [FloatParameter(name="a", min_value=1, max_value=3, helptext="bla")]

def test_float_norange():
    def f(a: float): pass

    with pytest.raises(Error):
        p(f)

def test_float_help_norange():
    def f(a: Annotated[float, Help("bla")]): pass

    with pytest.raises(Error):
        p(f)

