from typing import Annotated, Literal

from openswebcad import IncompatibleParametersError, Range, Help
from muscad import Cylinder, Union

def generate(
        metric: Literal["M4", "M6", "M8"], 
        length: Annotated[float, Range(10.0, 100.0), Help("length of the screw (lower part only)")], 
        count: Annotated[int, Range(1, 4)],
        ) -> str:
    diameter, head_diameter, head_height = {
                    "M4": (4.0, 7.0, 4.0),
                    "M6": (6.0, 10.0, 6.0),
                    "M8": (8.0, 13.0, 8.0),
            }[metric]
    main = Cylinder(h=length, d=diameter)
    head = Cylinder(h=head_height, d=head_diameter).align(top=main.top)
    screw = main + head
    root = Union()
    distance = 10.0
    for i in range(count):
        root += screw.translate(x=i*distance)

    if count > 1 and head_diameter + 1.0 > distance :
        raise IncompatibleParametersError(["count", "metric"], "not possible to generate multiple screws - objects would collide")
    number = 1/(count-4) # enforce division by zero to check exception
    return str(root)

