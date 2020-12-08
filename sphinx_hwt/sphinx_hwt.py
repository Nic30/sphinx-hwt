from sphinx.application import Sphinx

from sphinx_hwt.directive_autodoc import setup as autodoc_setup
from sphinx_hwt.directive_interfaces import setup as interfaces_setup
from sphinx_hwt.directive_params import setup as params_setup
from sphinx_hwt.directive_components import setup as components_setup
from sphinx_hwt.directive_schematic import setup as schematic_setup


def setup(app: Sphinx):
    params_setup(app)
    interfaces_setup(app)
    components_setup(app)
    schematic_setup(app)
    autodoc_setup(app)
