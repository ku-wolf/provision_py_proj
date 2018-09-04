"""provision_py_proj utils."""

import click
from provision_py_proj.config_manager import load_default, set_defaults, print_defaults
from functools import partial, update_wrapper

# Option keys
name_key = "option_name"
kwargs_key = "kwargs"
type_key = "type"
help_key = "help"
prompt_key = "prompt"
default_key = "default"
alts_key = "alts"
no_default_key = "no_default"
nargs_key = "nargs"
is_flag_key = "is_flag"
required_key = "required"
multiple_key = "multiple"

default_arg_delimeter = "_"


def create_option(
    name,
    previous_options,
    arg_delimiter=default_arg_delimeter,
    alts=None
):
    """Create option name with alternates."""
    if not alts:
        alts = [name[0]]

    options = [name]
    for alt in alts:
        start = "--"
        if len(alt) == 1:
            start = "-"
        options.append(start + str(alt))

    name = "".join(name.split(arg_delimiter))
    options.append("--" + str(name))

    ret = []
    for o in options:
        if o not in previous_options:
            ret.append(o)
            previous_options.add(o)

    return ret


def create_help_msg(name, arg_delimiter=default_arg_delimeter, default=None):
    """Create default option help msg."""
    name = " ".join(name.split(arg_delimiter))
    ret = "Set \"{option_name}\" value.".format(
        option_name=name
    )

    if default:
        ret += " Default is \"{default}\"" .format(
            default=default,
        )
    return ret + "\n"


def make_click_command(
        pkg_name,
        base_func,
        options=[],
        args=[],
        pass_context=False,
        default_prompt=False,
        set_defaults=False,
        group=None,
        arg_delimiter=default_arg_delimeter,
        alt_default_sources=[],

):
    """Make a click command with given options."""
    if group is None:
        group = click

    if pass_context:
        base_func = click.pass_context(base_func)

    previous_options = set()
    for option in options:
        name = option[name_key]
        alt_names = option.get(alts_key)
        kwargs = option[kwargs_key]

        if set_defaults:
            kwargs[default_key] = load_default(
                pkg_name,
                name,
                alt_default_sources
            )

        kwargs_vals = [
            (help_key, create_help_msg(name, kwargs.get(default_key)))
        ]

        if default_prompt:
            kwargs_vals.append(
                (prompt_key, " ".join(name.split(arg_delimiter)).title())
            )

        for kv in kwargs_vals:
            key, val = kv
            if key not in kwargs:
                kwargs[key] = val

        base_func = click.option(
            *create_option(name, previous_options, alts=alt_names),
            **kwargs
        )(base_func)

    for arg in args:
        name = arg[name_key]
        kwargs = arg[kwargs_key]
        base_func = click.argument(
            name,
            **kwargs
        )(base_func)

    return group.command()(base_func)


def wrapped_partial(func, *args, **kwargs):
    """Ensure partial app of func has __doc__ and __name__ attributes."""
    return update_wrapper(partial(func, *args, **kwargs), func)


def create_set_defaults_command(pkg_name, *args, **kwargs):
    """Create a command which sets defaults for pkg."""
    return make_click_command(
        pkg_name,
        wrapped_partial(set_defaults, pkg_name),
        *args,
        set_defaults=True,
        default_prompt=True,
        **kwargs
    )


def create_print_defaults_command(pkg_name, *args, **kwargs):
    """Create a command which prints defaults for pkg."""
    return make_click_command(
        pkg_name,
        wrapped_partial(print_defaults, pkg_name),
        *args,
        **kwargs
    )


def ask_user(question):
    """Ask user for yes no answer to question."""
    invalid_msg = "Please enter valid input."

    if not question.endswith("?"):
        question += "?"

    check = str(
        input("{question} (Y/N): ".format(question=question))
    ).lower().strip()

    try:
        if check[0] == "y":
            return True
        elif check[0] == "n":
            return False
        else:
            print(invalid_msg)
            return ask_user(question)
    except Exception:
        print(invalid_msg)
        return ask_user(question)
