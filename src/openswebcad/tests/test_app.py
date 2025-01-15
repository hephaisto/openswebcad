from typing import Literal, Annotated
import asyncio
from unittest.mock import MagicMock, patch, ANY

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

async def open_test_page(user: User):
    init()
    await user.open("/")
    user.find("testname").click()

async def test_parameter_list(user: User) -> None:
    await open_test_page(user)
    await user.should_see("length")
    await user.should_see("metric")
    await user.should_see("M4")
    await user.should_see("M6")
    await user.should_see("M8")
    await user.should_see("count")

async def test_float_parameter(user: User) -> None:
    await open_test_page(user)
    with patch.object(default_models[0], "generate") as generate:
        user.find("length").elements.pop().value=20.0
        await asyncio.sleep(1.0)
    generate.assert_called_once_with(length=20.0, metric=ANY, count=ANY)


async def test_int_parameter(user: User) -> None:
    await open_test_page(user)
    with patch.object(default_models[0], "generate") as generate:
        user.find("count").elements.pop().value=2
        await asyncio.sleep(1.0)
    generate.assert_called_once_with(count=2, length=ANY, metric=ANY)

# TODO: test choice
"""
async def test_choice_parameter(user: User) -> None:
    await open_test_page(user)
    with patch.object(default_models[0], "generate") as generate:
        user.find("M6").click()
    generate.assert_called_once_with(metric="M6", length=ANY, count=ANY)
"""

# TODO: test a) error propagation on change b) error propagation on generation for 1) assertion/arbitrary errors 2) incompatible parameter errors

"""
def raise_error(*args, **kwargs):
    raise RuntimeError("errortext")

async def test_error_propagation_on_change(user: User) -> None:
    await open_test_page(user)
    with patch.object(default_models[0], "generate", new=raise_error) as generate:
        user.find("count").elements.pop().value=2
    #log = user.find(ui.log).elements.pop()
    await asyncio.sleep(0.3)
    await user.should_see("model generation failed")
"""


async def test_preview(user: User):
    await open_test_page(user)
    image = user.find(ui.image).elements.pop()
    old = image.source
    user.find("length").elements.pop().value=20.0
    await asyncio.sleep(1.0)
    new = image.source
    assert new != old

async def test_generation(user: User):
    await open_test_page(user)
    user.find("generate STL").click()
    response = await user.download.next()
    assert response.status_code == 200
    assert len(response.content) > 100

