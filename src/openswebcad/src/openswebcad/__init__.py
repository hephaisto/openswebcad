from abc import ABC
from pydantic import BaseModel

from openswebcad.annotations import *

class GenerationError(RuntimeError):
    pass

class OpenScadScriptError(GenerationError):
    def __init__(self, script: str, stderr: str):
        self.script = script
        self.stderr = stderr

    def __str__(self):
        return "model generation failed"

class IncompatibleParametersError(GenerationError):
    def __init__(self, parameters: list[str], message: str):
        self.parameters = parameters
        self.message = message

    def __str__(self):
        separator = ": " if self.message else ""
        return "The following parameters have incompatible values: " + ', '.join(self.parameters) + separator + self.message

class ModelError(GenerationError):
    def __str__(self):
        return "model generation failed"

