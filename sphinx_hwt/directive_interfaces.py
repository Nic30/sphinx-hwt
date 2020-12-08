from docutils import nodes
from docutils.parsers.rst import Directive
import logging
from sphinx.application import Sphinx
from sphinx.locale import _
from sphinx.util import typing
from typing import Dict, List, Optional

from hwt.synthesizer.interface import Interface
from hwt.synthesizer.unit import Unit
from sphinx_hwt.utils import get_absolute_name_of_class_of_node, hwt_objs, merge_variable_lists_into_hwt_objs, \
    get_instance_from_directive_node


class hwt_interfaces(hwt_objs):
    """
    A directive which adds a list of HDL defined interfaces for Unit innstances
    The message also contains information about default value and type of the parameter.
    """

    def __init__(self, intf_list: List[Interface], extra_doc: Optional[Dict[str, List[nodes.Element]]]=None, rawsource='', *children, **attributes):
        super(hwt_interfaces, self).__init__(intf_list, extra_doc, rawsource, *children, **attributes)

    @staticmethod
    def obj_get_name(o: Interface):
        return o._name

    @staticmethod
    def visit_html(self, node: "hwt_interfaces"):
        """
        Generate html elements and schematic json
        """
        if not node.obj_list:
            return

        field_list = nodes.field_list()
        node += field_list

        params_list = nodes.bullet_list()
        of_type = _('of type')
        for i in sorted(node.obj_list, key=node.obj_get_name):
            i_p = nodes.paragraph()
            name = node.obj_get_name(i)
            i_p += nodes.strong(name, name)

            dt = getattr(i, "_dtype", None)
            t = typing.stringify(i.__class__)
            if dt is not None:
                t = f"{t} with dtype={dt}"
            annotation = f" - {of_type} {t}\n"
            i_p += nodes.Text(annotation)

            extra = node.extra_doc.get(name, None)
            if extra:
                i_p += extra

            params_list += nodes.list_item('', i_p)

        params_desc = nodes.field()
        params_desc += nodes.field_name(_('HDL IO'), _('HDL IO'))
        field_list += params_desc
        field_list += nodes.field_body('', params_list)

    @staticmethod
    def depart_html(self, node: "hwt_interfaces"):
        pass


class HwtInterfacesDirective(Directive):
    optional_arguments = 1
    final_argument_whitespace = False
    has_content = False

    def run(self):
        interface_list = []
        try:
            u = get_instance_from_directive_node(self, (Interface, Unit))
            u._loadDeclarations()
            interface_list = u._interfaces
        except Exception as e:
            absolute_name = get_absolute_name_of_class_of_node(self.state)
            logging.error(e, exc_info=True)
            raise Exception(
                "Error  occured while processing of %s" % absolute_name)

        interfaces = hwt_interfaces(interface_list)

        self.state.nested_parse(self.content,
                    self.content_offset,
                    interfaces)
        return [interfaces, ]


def merge_variable_lists_into_hwt_interfaces(app: Sphinx, domain: str, objtype: str, contentnode: nodes.Element):
    return merge_variable_lists_into_hwt_objs(app, domain, objtype, contentnode, hwt_interfaces)


def setup(app: Sphinx):
    app.connect('object-description-transform', merge_variable_lists_into_hwt_interfaces)
    app.add_node(hwt_interfaces,
                 html=(hwt_interfaces.visit_html,
                       hwt_interfaces.depart_html))
    app.add_directive('hwt-interfaces', HwtInterfacesDirective)
