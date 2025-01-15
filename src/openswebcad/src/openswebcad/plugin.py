import logging
import os
import importlib
import inspect
import typing
from openswebcad.parameters import Parameter, ChoiceParameter, IntParameter, FloatParameter, Model
from openswebcad import Range, Help


_logger = logging.getLogger(__name__)

def _could_be_plugin(filename: str):
    return not filename.startswith('.') and not filename.startswith('__') and filename.endswith('.py')

def load_plugin(path):
    module_name = os.path.split(path)[-1]
    if module_name.endswith(".py"):
        module_name = module_name[:-3]
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load_plugins(path: str) -> list:
    _logger.info(f"loading plugins from {path}")
    plugins = []
    for filename in sorted(os.listdir(path)):
        if _could_be_plugin(filename):
            try:
                plugin = load_plugin(os.path.join(path, filename))
                _logger.debug(f"loaded plugin {plugin.__name__}")
                plugins.append(plugin)
            except ImportError as e:
                _logger.error(f"unable to load plugin from {filename}: {e}")
    return plugins

def load_models(path: str) -> list:
    plugins = load_plugins(path)
    models = []
    for plugin in plugins:
        try:
            generator = plugin.generate
            _logger.debug(f"plugin {plugin.__name__} contains generate function")
            parameters = get_parameters(generator)
            model = Model(name=plugin.__name__, parameters=parameters, generate=generator)
            models.append(model)

        except AttributeError:
            _logger.debug(f"plugin {plugin.__name__} does not contain a generate function")
    _logger.info("loading models finished")
    return models

def find_annotation(annotation_class, annotations, default=None):
    filtered = [a for a in annotations if isinstance(a, annotation_class)]
    if len(filtered) == 0:
        if default:
            return default
        raise InvalidParameterAnnotation(f"required annotation {annotation_class} missing")
    if len(filtered) > 1:
        raise InvalidParameterAnnotation(f"multiple annotations of type {annotation_class}")
    return filtered[0]

class InvalidParameterAnnotation(RuntimeError):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

def parse_parameter(name: str, hint) -> Parameter:
    if isinstance(hint, typing._AnnotatedAlias):
        metadata = hint.__metadata__
        base = hint.__origin__
    else:
        metadata = []
        base = hint

    helptext = find_annotation(Help, metadata, Help(""))

    common_info = dict(name=name, helptext=helptext.text)

    if isinstance(base, typing._LiteralGenericAlias):
        return ChoiceParameter(**common_info, choices=base.__args__)
    for c, p in ((int, IntParameter), (float, FloatParameter)):
        if base == c:
            value_range = find_annotation(Range, metadata)
            if not (isinstance(value_range.min_value, c) and isinstance(value_range.max_value, c)):
                raise InvalidParameterAnnotation("invalid range annotation (wrong type)")
            return p(**common_info, min_value=value_range.min_value, max_value=value_range.max_value)
    raise InvalidParameterAnnotation(f"{name}: unknown parameter type: {base}")

def get_parameters(generator_func):
    return [parse_parameter(name, hint) for name, hint in inspect.get_annotations(generator_func).items() if name != "return"]


