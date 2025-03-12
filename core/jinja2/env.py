

from jinja2 import Environment, FileSystemLoader


env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True
)
