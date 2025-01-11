import argparse
import asyncio
import os
import logging

import openswebcad.plugin
import openswebcad.parameters
import openswebcad.generate

def parse_args(modelpath):
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=str)
    parser.add_argument("--format", choices=["stl", "png"], default="stl")
    parser.add_argument('--verbose', '-v', action='count', default=0)
    subparsers = parser.add_subparsers()

    models = openswebcad.plugin.load_models(modelpath)

    for model in models:
        parameters = model.parameters
        subparser = subparsers.add_parser(model.name)
        subparser.set_defaults(model=model)
        for p in parameters:
            if isinstance(p, openswebcad.parameters.ChoiceParameter):
                subparser.add_argument(f"--{p.name}", choices=p.choices, required=True)
            elif isinstance(p, openswebcad.parameters.IntParameter):
                subparser.add_argument(f"--{p.name}", type=int, required=True)
            elif isinstance(p, openswebcad.parameters.FloatParameter):
                subparser.add_argument(f"--{p.name}", type=float, required=True)
            else:
                raise NotImplementedError()
    return parser.parse_args()

def main():
    args = parse_args(get_model_path())
    logging.basicConfig(level={0: logging.WARN, 1: logging.INFO, 2: logging.DEBUG}[args.verbose])

    model = args.model
    model_parameters = {p.name: vars(args)[p.name] for p in model.parameters}
    script = model.generate(**model_parameters)
    result = asyncio.run(openswebcad.generate.generate_openscad(script, out_format=args.format, image_size=(800, 600)))
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, "wb") as f:
        f.write(result)

def get_model_path():
    try:
        return os.environ["OPENSWEBCAD_MODEL_PATH"]
    except KeyError:
        result = "."
        logging.warning(f"no OPENSWEBCAD_MODEL_PATH set, defaulting to {result}")
        return result

main()
