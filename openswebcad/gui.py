from typing import Any, Callable
import base64
import argparse
import logging
import traceback
from contextlib import contextmanager

from nicegui import ui

import openswebcad
import openswebcad.generate
import openswebcad.plugin
from openswebcad.parameters import Parameter, IntParameter, FloatParameter, ChoiceParameter

def generator(model, image, parameters: list[tuple[str, Parameter , Any]]):
    def generate():
        print("generating")
        model_parameters = {p[0]: p[2].value for p in parameters}
        for name, parameter in model_parameters.items():
            print(f"{name} = {parameter}")
        png = model.generate(out_format="png", **model_parameters)
        image_content = "data:image/png;base64," + base64.b64encode(png).decode()
        image.source = image_content
    return generate

class Generator:
    image_size: tuple[int, int] = 640, 480
    def __init__(self, model):
        self.model = model
        self.image = None
        self.parameters: list[tuple[str, Parameter , Any]] = []
        self.logger = logging.getLogger(f"{__name__}_{model.name}_{ui.context.client.id}")

    def get_parameter_array(self):
        model_parameters = {}
        for p in self.parameters:
            value = p[2].value
            if isinstance(p[1], IntParameter):
                value = int(value)
            model_parameters[p[0]] = value
        for name, parameter in model_parameters.items():
            self.logger.debug(f"{name} = {parameter}")
        return model_parameters

    def log_error(self, e: Exception):
        tb = traceback.format_exception(e.__class__, e, e.__traceback__)
        tb_lines = []
        for line in [line.rstrip('\n') for line in tb]:
            tb_lines.extend(line.splitlines())
        for line in tb_lines:
            self.logger.error(line)
        if isinstance(e, openswebcad.OpenScadScriptError):
            self.logger.debug("openscad script:")
            self.logger.debug(e.script)
            self.logger.debug("openscad error output:")
            self.logger.debug(e.stderr)
            
    
    def generate_scad(self):
        try:
            return self.model.generate(**self.get_parameter_array())
        except openswebcad.IncompatibleParametersError:
            raise # propagate explicit errors
        except Exception as e:
            raise openswebcad.ModelError from e

    async def generate_image(self):
        try:
            png = await openswebcad.generate.generate_openscad(script=self.generate_scad(), out_format="png", image_size=self.image_size)
            image_content = "data:image/png;base64," + base64.b64encode(png).decode()
            self.image.source = image_content
        except openswebcad.GenerationError as e:
            ui.notify(str(e), type="warning")
            self.log_error(e)

    async def generate_stl(self):
        try:
            self.logger.info("started rendering STL")
            stl = await openswebcad.generate.generate_openscad(script=self.generate_scad(), out_format="stl")
            filename = self.model.name + "_".join((f"{p[0]}_{p[2].value}" for p in self.parameters)) + ".stl"
            self.logger.info("rendering finished, download ready")
            ui.download(stl, filename)
        except openswebcad.GenerationError as e:
            ui.notify(str(e), type="warning")
            self.log_error(e)


class LogElementHandler(logging.Handler):
    """A logging handler that emits messages to a log element."""

    def __init__(self, element: ui.log):
        self.element = element
        super().__init__(logging.NOTSET)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.element.push(msg)
        except Exception:
            self.handleError(record)

@contextmanager
def disable(button: ui.button):
    button.disable()
    try:
        yield
    finally:
        button.enable()

async def with_disabled_button(button: ui.button, f: Callable) -> None:
    with disable(button):
        await f()


def make_generation_page(model, gui_log):
    generator = Generator(model)
    with ui.row(wrap=False):
        with ui.column():
            for p in model.parameters:
                if isinstance(p, ChoiceParameter):
                    ui.label(p.name)
                    e = ui.toggle(p.choices, value=p.choices[0], on_change=generator.generate_image)
                elif isinstance(p, IntParameter):
                    e = ui.number(label=p.name, value=p.min_value, min=p.min_value, max=p.max_value, format="%i", on_change=generator.generate_image, precision=0, validation={
                        "whole number": lambda v: float(int(v)) == v,
                        })
                elif isinstance(p, FloatParameter):
                    e = ui.number(label=p.name, value=p.min_value, min=p.min_value, max=p.max_value, format="%.1f", on_change=generator.generate_image, precision=1, validation=None)
                else:
                    raise NotImplementedError()
                assert e
                generator.parameters.append((p.name, p, e))

            ui.button("generate STL", on_click=lambda e: with_disabled_button(e.sender, generator.generate_stl))
    
        generator.image = ui.image().props("width={0}px height={1}px".format(*Generator.image_size))

    if gui_log:
        logger = ui.log().classes("w-full")
        handler = LogElementHandler(logger)
        generator.logger.addHandler(handler)
        ui.context.client.on_disconnect(lambda l=generator.logger, h=handler: l.removeHandler(h))

    generator.generate_image()



def app(native: bool, gui_log: bool, models: list):
    tab_list = []

    with ui.tabs().classes("w-full") as tabs:
        for model in models:
            tab_list.append(ui.tab(model.name))
    with ui.tab_panels(tabs).classes("w-full"):
        for tab, model in zip(tab_list, models):
            with ui.tab_panel(tab):
                make_generation_page(model, gui_log)
    ui.run(native=native)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", default=0, help="increase verbosity (can be used multiple times)")
    parser.add_argument("--native", "-n", action="store_true", help="use native GUI (window) instead of launching a webserver")
    parser.add_argument("--log", "-l", action="store_true", help="enable log output on GUI. Leaks internal information, but good for debugging")
    parser.add_argument("modelpath", type=str, help="the path to load plugins from")
    args = parser.parse_args()
    logging.basicConfig(level={0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}[args.verbose])
    return args

def main():
    args = parse_args()
    Generator.image_size = 1024, 768
    models = openswebcad.plugin.load_models(args.modelpath)
    if len(models) == 0:
        raise RuntimeError("no models found")
    app(native=args.native, gui_log=args.log, models=models)

main()
