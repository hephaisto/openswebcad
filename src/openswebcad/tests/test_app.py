from typing import Literal, Annotated

from nicegui import ui
from nicegui.testing import User

from openswebcad import Range, Help
import openswebcad.gui
import openswebcad.parameters
import openswebcad.plugin

pytest_plugins = ['nicegui.testing.user_plugin']

def default_generator(
        metric: Literal["M4", "M6", "M8"], 
        length: Annotated[float, Range(10.0, 100.0), Help("length of the screw (lower part only)")], 
        count: Annotated[int, Range(1, 4)],
        ) -> str:
    d = {"M4": 4.0, "M6": 6.0, "M8": 8.0}[metric]
    parameters = f"""
    h={length};
    d={d};
    """
    objects = """
    cylinder(h=h, d=d);
    """
    return parameters + objects


default_models = [
    openswebcad.parameters.Model(
        name="testname",
        generate=default_generator,
        parameters=openswebcad.plugin.get_parameters(default_generator),
    ),
]

def init():
    models = default_models
    openswebcad.gui.startup(models=models, gui_log=True)


async def test_startup(user: User) -> None:
    init()
    await user.open("/")
    await user.should_see("testname")

