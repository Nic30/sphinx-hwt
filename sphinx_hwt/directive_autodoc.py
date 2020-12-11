import logging
from sphinx.application import Sphinx

from hwt.synthesizer.interface import Interface
from hwt.synthesizer.unit import Unit
from sphinx_hwt.utils import get_absolute_name_of_class_of_node, \
    get_instance_from_directive_node
from sphinx_hwt.directive_params import HwtParamsDirective
from sphinx_hwt.directive_interfaces import HwtInterfacesDirective
from sphinx_hwt.directive_schematic import HwtSchematicDirective
from sphinx_hwt.directive_components import HwtComponentsDirective


class HwtAutodocDirective(HwtSchematicDirective):

    def run(self):
        "Can not use multiple hwt-autodoc/hwt-schematic/hwt-params/hwt-interfaces in a single class"

        try:
            u = get_instance_from_directive_node(self, (Interface, Unit))
        except Exception as e:
            absolute_name = get_absolute_name_of_class_of_node(self.state)
            logging.error(e, exc_info=True)
            raise Exception(
                f"Error occured while processing of {absolute_name:s}")

        params = HwtParamsDirective.run(self)
        interfaces = HwtInterfacesDirective.run(self)

        if isinstance(u, Unit):
            components = HwtComponentsDirective.run(self)
            schemes = HwtSchematicDirective.run(self)
            return [*params, *interfaces, *components, *schemes]
        else:
            return [*params, *interfaces]


def setup(app: Sphinx):
    app.add_directive('hwt-autodoc', HwtAutodocDirective)

