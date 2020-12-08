from docutils import nodes
from docutils.parsers.rst import Directive
import logging
from sphinx.application import Sphinx
from sphinx.locale import _
from sphinx.util import typing

from hwt.synthesizer.interface import Interface
from hwt.synthesizer.unit import Unit
from sphinx_hwt.utils import get_absolute_name_of_class_of_node, \
    hwt_objs, merge_variable_lists_into_hwt_objs, \
    get_instance_from_directive_node


class hwt_params(hwt_objs):
    """
    A directive which adds a list of defined HDL parameters for Unit innstances
    The message also contains information about default value and type of the parameter.
    """

    @staticmethod
    def visit_html(self, node: "hwt_params"):
        """
        Generate html elements and schematic json
        """
        extra_doc = node["extra_doc"]
        obj_list = node["obj_list"]

        if not obj_list:
            return

        field_list = nodes.field_list()
        node += field_list

        params_list = nodes.bullet_list()
        def_val = _('default value')
        of_type = _('of type')
        for name, t, v in sorted(obj_list, key=lambda x: x[0]):
            p_p = nodes.paragraph()
            p_p += nodes.strong(name, name)
            annotation = f" - {def_val} {v} {of_type} {t}\n"
            p_p += nodes.Text(annotation)
            extra = extra_doc.get(name, None)
            if extra:
                p_p += extra

            params_list += nodes.list_item('', p_p)

        params_desc = nodes.field()
        params_desc += nodes.field_name(_('HDL params'), _('HDL params'))
        field_list += params_desc
        field_list += nodes.field_body('', params_list)

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
                "Error  occured while processing of %s" % absolute_name)

        params_serialized = []
        for p in u._params:
            name = p._name
            v = p.get_value()
            t = getattr(v, "_dtype", None)
            if t is None:
                t = v.__class__
                t = typing.stringify(t)
            else:
                t = repr(t)
            params_serialized.append((name, t, repr(v)))

        params = hwt_params(params_serialized)

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

