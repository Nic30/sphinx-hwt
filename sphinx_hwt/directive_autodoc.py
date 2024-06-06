import logging
from sphinx.application import Sphinx
from hwt.hwIO import HwIO
from hwt.hwModule import HwModule
from sphinx_hwt.utils import get_absolute_name_of_class_of_node, \
    get_instance_from_directive_node
from sphinx_hwt.directive_params import HwtParamsDirective
from sphinx_hwt.directive_io import HwtIODirective
from sphinx_hwt.directive_schematic import HwtSchematicDirective
from sphinx_hwt.directive_components import HwtComponentsDirective
from sphinx_hwt.directive_buildreport import HwtBuildreportDirective


class HwtAutodocDirective(HwtSchematicDirective):

    def run(self):
        "Can not use multiple hwt-autodoc/hwt-schematic/hwt-params/hwt-interfaces in a single class"

        try:
            m = get_instance_from_directive_node(self, (HwIO, HwModule))
        except Exception as e:
            absolute_name = get_absolute_name_of_class_of_node(self.state)
            logging.error(e, exc_info=True)
            raise Exception(
                f"Error occured while processing of {absolute_name:s}")

        params = HwtParamsDirective.run(self)
        interfaces = HwtIODirective.run(self)

        if isinstance(m, HwModule):
            components = HwtComponentsDirective.run(self)
            schemes = HwtSchematicDirective.run(self)
            build_report = HwtBuildreportDirective(
                self.name, self.arguments,
                self.options, self.content,
                self.lineno, self.content_offset,
                self.block_text, self.state,
                self.state_machine).run()
            return [*params, *interfaces, *components, *schemes, *build_report]
        else:
            return [*params, *interfaces]


def setup(app: Sphinx):
    app.add_directive('hwt-autodoc', HwtAutodocDirective)
