"""app utils"""
import inspect
import logging
import os
from collections import OrderedDict
from collections.abc import Iterable, Mapping
from datetime import datetime
from functools import wraps
from pathlib import Path

import click
import numpy as np

from atlas_commons.exceptions import AtlasCommonsError

EXISTING_FILE_PATH = click.Path(exists=True, readable=True, dir_okay=False, resolve_path=True)
EXISTING_DIR_PATH = click.Path(exists=True, readable=True, dir_okay=True, resolve_path=True)
LOG_DIRECTORY = "."
DATA_PATH = Path(__file__).parent / "data"
ABT_PATH = Path(__file__).parent.parent.parent


class ParameterContainer(OrderedDict):
    """A dict class used to contain and display the parameters"""

    def __repr__(self):
        """Better printing than the normal OrderedDict"""
        return ", ".join(str(key) + ":" + str(val) for key, val in self.items())

    __str__ = __repr__


def log_args(logger, handler_path=None):
    """A decorator used to redirect logger and log arguments"""

    def set_logger(function, logger_path=handler_path):

        if handler_path is None:
            logger_path = os.path.join(LOG_DIRECTORY, function.__name__ + ".log")

        @wraps(function)
        def wrapper(*args, **kw):
            logger.addHandler(logging.FileHandler(logger_path))
            param = ParameterContainer(inspect.signature(function).parameters)
            for name, arg in zip(inspect.signature(function).parameters, args):
                param[name] = arg
            for key, value in kw.items():
                param[key] = value
            date_str = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            logger.info(f"{date_str}:{function.__name__} args:[{param}]")
            function(*args, **kw)

        return wrapper

    return set_logger


# Atlas files consistency checks
# Copied from https://bbpcode.epfl.ch/code/#/admin/projects/nse/atlas-analysis,
# see atlas.py and utils.py.


def ensure_list(value):
    """Convert iterable / wrap scalar into list (strings are considered scalar)."""
    if isinstance(value, Iterable) and not isinstance(value, (str, Mapping)):
        return list(value)
    return [value]


def compare_all(data_sets, fun, comp):
    """Compares using comp all values extracted from data_sets using the fun access function

    Ex:
        compare_all(atlases, lambda x: x.raw.shape, comp=np.allclose)
    """
    try:
        res = all(comp(fun(data_sets[0]), fun(other)) for other in data_sets[1:])
    except Exception as error_:
        raise AtlasCommonsError("[compare_all] Bad operation during comparing") from error_
    return res


def assert_properties(atlases):
    """Assert that all atlases properties match

    Args:
        atlases: a list of voxeldata

    Raises:
        if one of the property is not shared by all data files
    """
    atlases = ensure_list(atlases)
    if not compare_all(atlases, lambda x: x.raw.shape, comp=np.allclose):
        raise AtlasCommonsError("Need to have the same shape for all files")
    if not compare_all(atlases, lambda x: x.voxel_dimensions, comp=np.allclose):
        raise AtlasCommonsError("Need to have the same voxel_dimensions for all files")
    if not compare_all(atlases, lambda x: x.offset, comp=np.allclose):
        raise AtlasCommonsError("Need to have the same offset for all files")


def assert_meta_properties(atlases):
    """Assert that all VoxelData metadata match

    Check that
        - VoxelData.shape
        - VoxelData.voxel_dimensions
        - VoxelData.offset

    is consistent accross the input VoxelData objects.

    For instance, it will not raise when comparing annotations with numpy shape
    (W, H, D) to direction vectors with numpy shape (W, H, D, 3).

    Args:
        atlases: a list of VoxelData objects

    Raises:
        if one of the above meta properties is not shared by all VoxelData objects.
    """
    atlases = ensure_list(atlases)
    if not compare_all(atlases, lambda x: x.shape, comp=np.allclose):
        raise AtlasCommonsError("Need to have the same shape for all files")
    if not compare_all(atlases, lambda x: x.voxel_dimensions, comp=np.allclose):
        raise AtlasCommonsError("Need to have the same voxel_dimensions for all files")
    if not compare_all(atlases, lambda x: x.offset, comp=np.allclose):
        raise AtlasCommonsError("Need to have the same offset for all files")


def common_atlas_options(function):
    """
    Common atlas options.

    Args:
        function: the command function to be wrapped with common options.

    Returns:
        the `function` decorated with the common options.
        Example usage in app:
            @app.command()
            @common_atlas_options
            @click.option(...)
            ...
            def combine_annotations(annotation_path, hierarchy_path, ...):
    """
    function = click.option(
        "--annotation-path",
        type=EXISTING_FILE_PATH,
        required=True,
        help=(
            "The path to the whole mouse brain annotation file (nrrd). See the main command "
            "description for possible restrictions."
        ),
    )(function)
    function = click.option(
        "--hierarchy-path",
        type=EXISTING_FILE_PATH,
        required=True,
        help="The path to the hierarchy file, i.e., AIBS 1.json or BBP hierarchy.json.",
    )(function)

    return function


def set_verbose(logger, verbose):
    """Set the verbose level for the cli"""
    logger.setLevel((logging.WARNING, logging.INFO, logging.DEBUG)[min(verbose, 2)])


def verbose_option(function):
    """
    Common verbose option for atlas related CLIs.

    Args:
        function: the command function to be wrapped with the verbose option.

    Returns:
        the `function` decorated with the common options.
        Example usage in app:
            L = logging.getLogger(__name__)
            ...
            @app.command()
            @verbose_option
            @click.option(...)
            ...
            def combine_annotations(verbose, ...):
                set_verbose(L, verbose)
    """
    function = click.option(
        "-v",
        "--verbose",
        count=True,
        required=False,
        help="Use -v for info and -vv for debug. Defaults to warning level.",
    )(function)

    return function
