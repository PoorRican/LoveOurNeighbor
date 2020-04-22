   ██████                      ██          ██ ██                ██   ██                 
  ██░░░░██                    ░██         ░░ ░██               ░██  ░░            █████ 
 ██    ░░   ██████  ███████  ██████ ██████ ██░██      ██   ██ ██████ ██ ███████  ██░░░██
░██        ██░░░░██░░██░░░██░░░██░ ░░██░░█░██░██████ ░██  ░██░░░██░ ░██░░██░░░██░██  ░██
░██       ░██   ░██ ░██  ░██  ░██   ░██ ░ ░██░██░░░██░██  ░██  ░██  ░██ ░██  ░██░░██████
░░██    ██░██   ░██ ░██  ░██  ░██   ░██   ░██░██  ░██░██  ░██  ░██  ░██ ░██  ░██ ░░░░░██
 ░░██████ ░░██████  ███  ░██  ░░██ ░███   ░██░██████ ░░██████  ░░██ ░██ ███  ░██  █████ 
  ░░░░░░   ░░░░░░  ░░░   ░░    ░░  ░░░    ░░ ░░░░░    ░░░░░░    ░░  ░░ ░░░   ░░  ░░░░░  
  
  
Thank you for your willingness to contribute to the LON codebase. This is a basic guide to the layout of the code,
and the coding standards.

# Coding style

For python code, please follow the [style guidelines set by Django](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/).
Consider using [pylint-django](https://github.com/PyCQA/pylint-django) for static analysis.

As for docstrings, please follow the [numpydoc docstring guide](https://numpydoc.readthedocs.io/en/latest/format.html).

# Organization / Descriptions

## Django App

The main django app is in a directory `frontend`. The main templating language used in the entire website is Jinja2.
It is similar to the django template language, but cannot make use of 3rd party's apps' tags. While this is could be seen
as an inconvenience, the file 'jinja.py' defines what tags, functions, and variables are globally available in the
template context. Jinja2 was chosen for its use of macros. Another benefit of Jinja2 is reduced memory usage from fine-tuning
the environment defined in 'jinja.py'.

As of now, all templates are in a directory labeled `templates`, and organized by the module that uses them. This directory
is all Jinja2 templates. Django-templates will not work in this directory. The directory 'macros' contains all macros used in
the templates. Macros must be explicitly imported in the template they are used in. Even though the macros are reusable, not
all of them are used more than once.

The directory 'layout' contains macros used to build the layout (e.g: the header and footer),
and are typically used in 'layout.html'. The directory 'parts' has all other macros and are 
  
## Module Hierarchy

Users and user-accounts are managed in the `people` module. Here, the `User` model inherits built-in django.contrib.auth
functionality. This was chosen to have more granular control over the templating, properties and redirection. It is
intended to reduce the "black-box" of built-in objects and methods. There is no special object for ministry administrators.

The `ministry` and `campaign` modules define the functionality for ministries and their campaigns, respectively.
Even though these two modules import many of each others objects and or methods, they have been separated for to remain
organized. The functionality for news is in a separate module, named `news`.
