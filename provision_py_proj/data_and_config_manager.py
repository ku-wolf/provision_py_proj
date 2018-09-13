"""Utils for saving and loading package config/data."""

import pickle
import os
from appdirs import user_config_dir, user_data_dir
from functools import wraps

defaults_file_name = "defaults"
config_dir = None
defaults = {}


def create_config_dir_name(pkg_name):
    """Return name of pkg's config directory."""
    return os.path.join(user_config_dir(), pkg_name + "_config")


def create_data_dir_name(pkg_name):
    """Return name of pkg's data directory."""
    return os.path.join(user_data_dir(), pkg_name + "_data")


def load_pickle(file_path):
    """Load pickle object."""
    with open(file_path, "rb") as d:
        return pickle.load(d)


def dump_pickle(obj, file_name, *args, **kwargs):
    """Dump pickle object."""
    with open(file_name, "wb") as d:
        pickle.dump(obj, d, *args, **kwargs)


def pass_config_path(f):
    """Pass defaults file path to f."""
    @wraps(f)
    def wrapper(pkg_name, *args, **kwargs):
        config_dir = create_config_dir_name(pkg_name)
        return f(pkg_name, *args, config_dir=config_dir, **kwargs)

    return wrapper


@pass_config_path
def load_config(pkg_name, file_name, config_dir):
    """Load file from config dir."""
    return load_pickle(os.path.join(config_dir, file_name))


@pass_config_path
def dump_config(pkg_name, obj, target, config_dir):
    """Dump config."""
    dump_pickle(obj, os.path.join(config_dir, target))


def load_defaults(pkg_name):
    """Load defaults."""
    if pkg_name not in defaults:
        defaults[pkg_name] = load_config(pkg_name, defaults_file_name)
    return defaults[pkg_name]


def save_defaults(pkg_name, obj):
    """Load defaults."""
    defaults[pkg_name] = obj
    return dump_config(pkg_name, obj, defaults_file_name)


def load_default(pkg_name, name, alt_default_sources):
    """Load default for name."""
    default = load_defaults(pkg_name).get(name)
    if default is None and name in alt_default_sources:
            return alt_default_sources[name]()
    return default


def print_defaults(pkg_name):
    """Print provisioner defaults."""
    for k, v in load_defaults(pkg_name).items():
        print("{key}: {value}".format(key=k, value=v))


def set_defaults(pkg_name, **kwargs):
    """Set provisioner defaults."""
    defaults = load_defaults(pkg_name)
    for k, v in kwargs.items():
        if k in defaults:
            defaults[k] = v
    save_defaults(pkg_name, defaults)
