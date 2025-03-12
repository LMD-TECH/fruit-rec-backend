

from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape


env = Environment(
    # Chargeur de templates depuis un dossier
    loader=FileSystemLoader("templates"),
    autoescape=True,  # Active l'auto-échappement (utile pour HTML)
    trim_blocks=True,  # Supprime les espaces blancs inutiles
    lstrip_blocks=True  # Supprime les espaces au début des blocs
)
