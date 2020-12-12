from docutils import nodes
from docutils.parsers.rst import Directive
import logging
from sphinx.application import Sphinx
from sphinx.locale import _
from hwt.synthesizer.interface import Interface
from hwt.synthesizer.unit import Unit
from sphinx_hwt.utils import get_absolute_name_of_class_of_node, \
    hwt_objs, merge_variable_lists_into_hwt_objs, \
    get_instance_from_directive_node, construct_property_description_list, \
    ref_to_class


class hwt_params(hwt_objs):
    """
    A directive which adds a list of defined HDL parameters for Unit instances
    The message also contains information about default value and type of the parameter.
    """

    @staticmethod
    def visit_html(self, node: "hwt_params"):
        pass

    @staticmethod
    def depart_html(self, node: "hwt_params"):
        pass


class HwtParamsDirective(Directive):
    optional_arguments = 1
    final_argument_whitespace = False
    has_content = False

    def run(self):
        try:
            u = get_instance_from_directive_node(self, (Interface, Unit))
        except Exception as e:
            absolute_name = get_absolute_name_of_class_of_node(self.state)
            logging.error(e, exc_info=True)
            raise Exception(
                f"Error occured while processing of {absolute_name:s}")

        if not u._params:
            return []

        description_group_list, obj_list = construct_property_description_list('HDL params')
        def_val = _('default value')
        of_type = _('of type')
        name_to_descr_paragraph = {}
        for p in u._params:
            name = p._name
            v = p.get_value()
            t = getattr(v, "_dtype", None)
            if t is None:
                t = ref_to_class(v.__class__)
            else:
                t = nodes.Text(repr(t))

            descr_p = nodes.paragraph()
            descr_p += nodes.strong(name, name)
            descr_p += nodes.Text(f" - {def_val} {v} {of_type} ")
            descr_p += t

            obj_list += nodes.list_item('', descr_p)

            name_to_descr_paragraph[name] = descr_p

        params = hwt_params(name_to_descr_paragraph)
        params += description_group_list

        self.state.nested_parse(self.content,
                    self.content_offset,
                    params)
        return [params, ]


def merge_variable_lists_into_hwt_params(app: Sphinx, domain: str, objtype: str, contentnode: nodes.Element):
    return merge_variable_lists_into_hwt_objs(app, domain, objtype, contentnode, hwt_params)


def setup(app: Sphinx):
    app.connect('object-description-transform', merge_variable_lists_into_hwt_params)
    app.add_node(hwt_params,
                 html=(hwt_params.visit_html,
                       hwt_params.depart_html))
    app.add_directive('hwt-params', HwtParamsDirective)

