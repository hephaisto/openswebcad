from typing import Annotated

from openswebcad import IncompatibleParametersError, Range, Help

def generate(
        length: Annotated[float, Range(10.0, 100.0), Help("length of the screw (lower part only)")], 
        ) -> str:
    parameters = f"h={length};"
    objects = """
    cylinder(h=h, r=3.0);
    """
    return parameters + objects
