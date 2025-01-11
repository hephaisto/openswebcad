from typing import Callable

from pydantic import BaseModel

class Parameter(BaseModel):
    name: str
    helptext: str = ""

class ChoiceParameter(Parameter):
    choices: list[str]

class IntParameter(Parameter):
    min_value: int
    max_value: int

class FloatParameter(Parameter):
    min_value: float
    max_value: float

class Model(BaseModel):
    name: str
    generate: Callable
    parameters: list[Parameter]

