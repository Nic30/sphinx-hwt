from docutils import nodes
from docutils.parsers.rst import Directive
import logging
from sphinx.application import Sphinx
from sphinx.locale import _

from hwt.synthesizer.unit import Unit
from hwt.synthesizer.utils import synthesised
from hwtGraph.elk.fromHwt.defauts import DEFAULT_PLATFORM
from sphinx_hwt.utils import get_absolute_name_of_class_of_node, \
    hwt_objs, merge_variable_lists_into_hwt_objs, \
    get_instance_from_directive_node, construct_property_description_list,\
    ref_to_class


class hwt_components(hwt_objs):
    """
    A directive which adds a list of defined HDL components for Unit instances
    The message also contains information about default value and type of the parameter.
    """

    @staticmethod
    def visit_html(self, node: "hwt_components"):
        pass


    @staticmethod
    def depart_html(self, node: "hwt_components"):
        pass


class HwtComponentsDirective(Directive):
    optional_arguments = 1
    final_argument_whitespace = False
    has_content = False

    def run(self):
        try:
            u = get_instance_from_directive_node(self, Unit)
            synthesised(u, DEFAULT_PLATFORM)
        except Exception as e:
            absolute_name = get_absolute_name_of_class_of_node(self.state)
            logging.error(e, exc_info=True)
            raise Exception(
                f"Error occured while processing of {absolute_name:s}")

        if not u._units:
            return []

        description_group_list, obj_list = construct_property_description_list('HDL components')
        name_to_descr_paragraph = {}
        of_type = _('of type')
        for p in u._units:
            name = p._name

            p_p = nodes.paragraph()
            p_p += nodes.strong(name, name)
            p_p += nodes.Text(f" - {of_type} ")
            p_p += ref_to_class(p.__class__)
            obj_list += nodes.list_item('', p_p)
            name_to_descr_paragraph[name] = p_p

        components = hwt_components(name_to_descr_paragraph)
        components += description_group_list

        self.state.nested_parse(self.content,
                    self.content_offset,
                    components)
        return [components, ]


def merge_variable_lists_into_hwt_components(app: Sphinx, domain: str, objtype: str, contentnode: nodes.Element):
    return merge_variable_lists_into_hwt_objs(app, domain, objtype, contentnode, hwt_components)


def setup(app: Sphinx):
    app.connect('object-description-transform', merge_variable_lists_into_hwt_components)
    app.add_node(hwt_components,
                 html=(hwt_components.visit_html,
                       hwt_components.depart_html))
    app.add_directive('hwt-components', HwtComponentsDirective)

