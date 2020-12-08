import logging
from sphinx.application import Sphinx

from hwt.synthesizer.interface import Interface
from hwt.synthesizer.unit import Unit
from sphinx_hwt.utils import get_absolute_name_of_class_of_node, \
    get_instance_from_directive_node
from sphinx_hwt.directive_params import hwt_params
from sphinx_hwt.directive_interfaces import hwt_interfaces
from sphinx_hwt.directive_schematic import HwtSchematicDirective


class HwtAutodocDirective(HwtSchematicDirective):

    def run(self):
        try:
            u_for_io = get_instance_from_directive_node(self, (Interface, Unit))
        except Exception as e:
            absolute_name = get_absolute_name_of_class_of_node(self.state)
            logging.error(e, exc_info=True)
            raise Exception(
                "Error  occured while processing of %s" % absolute_name)

        params = hwt_params(u_for_io._params)
        self.state.nested_parse(self.content,
                    self.content_offset,
                    params)

        u_for_io._loadDeclarations()
        interfaces = hwt_interfaces(u_for_io._interfaces)
        self.state.nested_parse(self.content,
                    self.content_offset,
                    interfaces)

        if isinstance(u_for_io, Unit):
            schemes = HwtSchematicDirective.run(self)
            return [params, interfaces, *schemes]
        else:
            return [params, interfaces]


def setup(app: Sphinx):
    app.add_directive('hwt-autodoc', HwtAutodocDirective)

