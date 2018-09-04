#!/usr/bin/python3
"""Module for license management."""

import os
import shutil
from provision_py_proj import pkg_name
from provision_py_proj.config_manager import create_data_dir_name

license_dir_name = "licenses"
user_data_dir = create_data_dir_name(pkg_name)
license_dir = os.path.join(user_data_dir, license_dir_name)


def get_license_info(path=False):
    """Get license info."""
    for f in os.listdir(license_dir):
        ret = f
        if path:
            ret = os.path.join(license_dir, ret)
        yield ret


def get_license_paths():
    """Get paths to available licenses."""
    return get_license_info(path=True)


def get_license_names():
    """Get names of available licenses."""
    return get_license_info()


def print_licenses():
    """Print available licenses."""
    print("Available Licenses:")
    for l in get_license_names():
        print(l)


def get_latest_license():
    """Get most recently modified license in license dir."""
    min_mod, min_name = min(
        ((os.path.getmtime(f), f) for f in get_license_paths())
    )
    return os.path.basename(min_name)


def write_license(name=None, dest=None, path=None):
    """Write license to destination."""
    if path is None:
        path = os.path.join(license_dir, name)
    if dest is None:
        dest = license_dir
    shutil.copy2(path, dest)
