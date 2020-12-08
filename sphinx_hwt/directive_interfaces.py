from docutils import nodes
from docutils.parsers.rst import Directive
import logging
from sphinx.application import Sphinx
from sphinx.locale import _
from sphinx.util import typing

from hwt.synthesizer.interface import Interface
from hwt.synthesizer.unit import Unit
from sphinx_hwt.utils import get_absolute_name_of_class_of_node, hwt_objs, merge_variable_lists_into_hwt_objs, \
    get_instance_from_directive_node
from ipCorePackager.constants import INTF_DIRECTION, DIRECTION


class hwt_interfaces(hwt_objs):
    """
    A directive which adds a list of HDL defined interfaces for Unit innstances
    The message also contains information about default value and type of the parameter.
    """

    @staticmethod
    def visit_html(self, node: "hwt_interfaces"):
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
        of_type = _('of type')
        for name, type_str, v in sorted(obj_list, key=lambda x: x[0]):
            assert v is None
            i_p = nodes.paragraph()
            i_p += nodes.strong(name, name)

            annotation = f" - {of_type} {type_str}\n"
            i_p += nodes.Text(annotation)

            extra = extra_doc.get(name, None)
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
        try:
            u = get_instance_from_directive_node(self, (Interface, Unit))
            u._loadDeclarations()
        except Exception as e:
            absolute_name = get_absolute_name_of_class_of_node(self.state)
            logging.error(e, exc_info=True)
            raise Exception(
                "Error  occured while processing of %s" % absolute_name)

        interfaces_serialized = []
        for i in u._interfaces:
            name = i._name
            dt = getattr(i, "_dtype", None)
            t = typing.stringify(i.__class__)
            if dt is not None:
                t = f"{t} with dtype={dt}"
            d = INTF_DIRECTION.opposite(i._direction)
            t = f"{t} - {d.name}"
            if i._masterDir != DIRECTION.OUT:
                t = f"{t} (Master={i._masterDir.name})"

            interfaces_serialized.append((name, t, None))

        interfaces = hwt_interfaces(interfaces_serialized)

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
