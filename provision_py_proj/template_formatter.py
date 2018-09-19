#!/usr/bin/python3
"""Format templates for empty Py Pkg."""

import os
from provision_py_proj.pkg_utils import pkg_name
from provision_py_proj.data_and_config_manager import create_data_dir_location

user_data_dir = create_data_dir_location(pkg_name)
template_dir = os.path.join(user_data_dir, "templates")

general_name = "general"
specific_name = "specific"
template_locations = {
    general_name: os.path.join(template_dir, general_name),
    specific_name: os.path.join(template_dir, specific_name)
}


class Template:
    """Template class."""

    def __init__(self, template_name=None, target=None, file_stat=None, template_path=None, location=general_name):
        """Initialize template variables."""
        location = template_locations[location]
        self.template_name = make_template_name(template_name)
        self.template_path = template_path
        if self.template_path is None:
            self.template_path = os.path.join(location, self.template_name)
        if target:
            self.target = target
        self.file_stat = file_stat

    def write_formatted_template(self, **kwargs):
        """Format template with kwargs and write to target."""
        with open(self.template_path, "r") as template:
            with open(self.target, "w") as target:
                for l in template:
                    target.write(l.format(**kwargs))
            if self.file_stat:
                os.chmod(self.target, self.file_stat)


def make_template_name(base):
    """Create template name from base."""
    return base + "_tmpl"
