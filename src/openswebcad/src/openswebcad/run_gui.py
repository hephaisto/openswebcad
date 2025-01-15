import argparse
import logging

from nicegui import ui, app

import openswebcad.plugin
import openswebcad.gui

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
    openswebcad.gui.Generator.image_size = 1024, 768
    models = openswebcad.plugin.load_models(args.modelpath)
    if len(models) == 0:
        raise RuntimeError("no models found")

    app.on_startup(lambda: openswebcad.gui.startup(gui_log=args.log, models=models))
    ui.run(native=args.native)

main()
