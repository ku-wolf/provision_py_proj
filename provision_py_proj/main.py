#!/usr/bin/python3
"""Module for empty python pkg creation."""

import os
import click
import sys
import shutil
import copy
import stat
from subprocess import call
from provision_py_proj import pkg_name
from provision_py_proj.command_creator import *
from provision_py_proj.data_and_config_manager import load_defaults, create_data_dir_name, create_config_dir_name
from provision_py_proj.template_formatter import Template
from provision_py_proj.license_manager import get_license_names, write_license, get_latest_license, print_licenses


# Filenames

bin_dir = "bin"
test_dir = "test"
readme_name = "README.md"
setup_name = "setup.py"
manifest_name = "MANIFEST.in"
requirements_name = "requirements.txt"
init_file = "__init__.py"
license_file_name = "LICENSE.txt"
gitignore_name = ".gitignore"

arg_delimiter = "_"


def create_option_name(*args):
    """Create option name for provisioner."""
    return arg_delimiter.join(args)


# Option names
license_key = "license"
app_name_key = create_option_name("app", "name")
no_config_key = create_option_name("no", "config")
no_data_key = create_option_name("no", "data")
no_bin_key = create_option_name("no", "bin")
src_dir_key = create_option_name("src", "dir")
requirements_key = "requirements"
defaultable_key = "defaultable"

provisioner_options = [
    {
        name_key: "description",
        defaultable_key: True,
        kwargs_key: {}
    },
    {
        name_key: "url",
        defaultable_key: True,
        kwargs_key: {}
    },
    {
        name_key: "version",
        defaultable_key: True,
        kwargs_key: {}
    },
    {
        name_key: "author",
        alts_key: ["auth"],
        defaultable_key: True,
        kwargs_key: {}
    },
    {
        name_key: create_option_name("author", "email"),
        alts_key: ["email"],
        defaultable_key: True,
        kwargs_key: {}
    },
    {
        name_key: license_key,
        defaultable_key: True,
        kwargs_key: {
            type_key: click.Choice(list(get_license_names())),
        }
    },
    {
        name_key: create_option_name("python", "interpreter", "path"),
        alts_key: ["pip"],
        defaultable_key: True,
        kwargs_key: {
            prompt_key: False,
        }
    },
    {
        name_key: requirements_key,
        no_default_key: True,
        kwargs_key: {
            multiple_key: True,
            prompt_key: False
        }
    },
    {
        name_key: no_config_key,
        alts_key: ["nocnf"],
        kwargs_key: {
            is_flag_key: True,
            help_key: "Indicate package has no config and will not require {cnf} package.".format(cnf=pkg_name),
            prompt_key: False
        }
    },
    {
        name_key: no_data_key,
        kwargs_key: {
            is_flag_key: True,
            help_key: "Indicate package has no data and will not create data dirs.".format(cnf=pkg_name),
            prompt_key: False
        }

    },
    {
        name_key: no_bin_key,
        kwargs_key: {
            is_flag_key: True,
            help_key: "Indicate package has no command line interface.",
            prompt_key: False
        }
    },
    {
        name_key: src_dir_key,
        kwargs_key: {
            help_key: "Specify directory which contains src files.",
            prompt_key: False
        }
    },
]

set_defaults_options = copy.deepcopy(provisioner_options)
for o in set_defaults_options:
    defaultable = o.get(defaultable_key)
    if defaultable:
        try:
            del o[kwargs_key][prompt_key]
        except KeyError:
            pass

for o in set_defaults_options:
    o[kwargs_key][default_key] = ""

provisioner_options.append(
    {
        name_key: app_name_key,
        kwargs_key: {}
    }
)

add_license_args = [
    {
        name_key: "licenses",
        kwargs_key: {
            nargs_key: -1,
            required_key: True
        }
    }
]


alt_default_sources = {
    "license": get_latest_license
}


def format_empty_pkg_templates(app_dir, include_bin, **kwargs):
    """Format templates for empty py pkg."""
    setup_target = os.path.join(app_dir, setup_name)
    cmd_target = os.path.join(app_dir, bin_dir, app_dir)
    requirements_target = os.path.join(app_dir, requirements_name)
    manifest_target = os.path.join(app_dir, manifest_name)
    readme_target = os.path.join(app_dir, readme_name)
    gitignore_target = os.path.join(app_dir, gitignore_name)
    init_target = os.path.join(app_dir, app_dir, init_file)

    templates = [
        Template("setup", setup_target, stat.S_IRWXU),
        Template("requirements", requirements_target),
        Template("manifest", manifest_target),
        Template("readme", readme_target),
        Template("gitignore", gitignore_target),
        Template("init", init_target)
    ]

    if include_bin:
        templates.append(Template("cmd", cmd_target))

    for t in templates:
        t.write_formatted_template(**kwargs)


def rename_src(src_dir):
    i = 1
    suffix = "_provision_src"

    def create_new_name():
        end = "_" + str(i) if i > 1 else ""
        return str(src_dir) + suffix + end

    new_name = create_new_name()
    while os.path.exists(new_name):
        i += 1
        new_name = create_new_name()

    shutil.move(src_dir, new_name)
    return new_name
    

def provision(**kwargs):
    """Create files and dirs for empty py pkg."""
    # retrieve args
    app_name = kwargs.get(app_name_key)
    license = kwargs.get(license_key)
    no_bin = kwargs.get(no_bin_key)
    no_config = kwargs.get(no_config_key)
    no_data = kwargs.get(no_data_key)
    requirements = list(kwargs.get(requirements_key))
    old_src_dir = kwargs.get(src_dir_key)
    include_bin = not no_bin
    include_config = not no_config
    include_data = not no_data

    # define pkg structure
    bin_path = os.path.join(app_name, bin_dir)
    main_app_path = os.path.join(app_name, app_name)
    test_path = os.path.join(main_app_path, test_dir)
    data_path = os.path.join(main_app_path, create_data_dir_name(app_name))
    config_path = os.path.join(main_app_path, create_config_dir_name(app_name))


    #cp from src
    new_src_dir = None
    if old_src_dir is not None:
        try:
            if old_src_dir == app_name:
                new_src_dir = rename_src(old_src_dir)
            else:
                new_src_dir = old_src_dir
        except:
            if new_src_dir is not None:
                shutil.move(new_src_dir, old_src_dir)

    if os.path.exists(app_name):
        print(
            "App with name {app_name} already exists.".format(app_name=app_name)
        )
        rm = ask_user("Would you like to remove")
        if rm:
            shutil.rmtree(app_name)
        else:
            sys.exit(1)

    if new_src_dir is not None:
        shutil.copytree(new_src_dir, main_app_path)

    #create pkg structure
    paths_to_create = [app_name]
    if include_bin:
        paths_to_create.append(bin_path)
    if include_config:
        paths_to_create.append(config_path)
    if include_data:
        paths_to_create.append(data_path)

    python_pkg_dirs = [main_app_path, test_path]
    paths_to_create.extend(python_pkg_dirs)

    for path in paths_to_create:
        os.makedirs(path, exist_ok=True)

    for path in python_pkg_dirs:
        open(os.path.join(path, init_file), "a").close()

    #update requirements kwargs
    if include_config or include_data:
        requirements.append(pkg_name)
    kwargs[requirements_key] = requirements

    # build templates with kwargs
    format_empty_pkg_templates(
        app_name,
        script_dir=bin_dir,
        include_bin=include_bin,
        **kwargs
    )

    # cp license
    license_target = os.path.join(app_name, license_file_name)
    write_license(name=license, dest=license_target)


def add_licenses(licenses):
    """Add licenses to provisioner."""
    for l_path in licenses:
        write_license(path=l_path)


def main():
    pass

main.__doc__ = """

    Provision an empty Python package.

    Create empty Package with following structure:

    \b
    test_pkg
    ├── (bin)
    │   └── test_pkg
    ├── .gitignore
    ├── LICENSE.txt
    ├── MANIFEST.in
    ├── README.md
    ├── requirements.txt
    ├── setup.py
    └── test_pkg
        ├── __init__.py
        ├── (test_pkg_data)
        │   └── ...
        ├── (test_pkg_config)
        │   └── ...
        ├── test
            └── __init__.py

"""

main = click.group()(main)

provision = make_click_command(
    pkg_name,
    provision,
    options=provisioner_options,
    default_prompt=True,
    set_defaults=True,
    group=main
)
add_licenses = make_click_command(
    pkg_name,
    add_licenses,
    args=add_license_args,
    group=main
)
print_licenses = make_click_command(
    pkg_name,
    print_licenses,
    group=main
)
set_defaults = create_set_defaults_command(
    pkg_name,
    options=set_defaults_options,
    group=main
)
print_defaults = create_print_defaults_command(
    pkg_name,
    group=main
)
