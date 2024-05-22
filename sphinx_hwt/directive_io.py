from docutils import nodes
from docutils.parsers.rst import Directive
import logging
from sphinx.application import Sphinx
from sphinx.locale import _

from hwt.hwIO import HwIO
from hwt.hwModule import HwModule
from sphinx_hwt.utils import get_absolute_name_of_class_of_node, hwt_objs, merge_variable_lists_into_hwt_objs, \
    get_instance_from_directive_node, construct_property_description_list, \
    ref_to_class
from ipCorePackager.constants import INTF_DIRECTION, DIRECTION


class hwt_io(hwt_objs):
    """
    A directive which adds a list of HDL defined interfaces for HwModule instances
    The message also contains information about default value and type of the parameter.
    """

    @staticmethod
    def visit_html(self, node: "hwt_io"):
        pass

    @staticmethod
    def depart_html(self, node: "hwt_io"):
        pass


class HwtIODirective(Directive):
    optional_arguments = 1
    final_argument_whitespace = False
    has_content = False

    def run(self):
        try:
            m = get_instance_from_directive_node(self, (HwIO, HwModule))
            m._loadHwDeclarations()
        except Exception as e:
            absolute_name = get_absolute_name_of_class_of_node(self.state)
            logging.error(e, exc_info=True)
            raise Exception(
                f"Error occured while processing of {absolute_name:s}")
        if not m._hwIOs:
            return []

        is_HwModule = isinstance(m, HwModule)
        description_group_list, obj_list = construct_property_description_list('HDL IO')
        of_type = _('of type')
        io_name_to_descr_paragraph = {}
        for hwIO in m._hwIOs:
            name = hwIO._name

            i_p = nodes.paragraph()
            i_p += nodes.strong(name, name)

            i_p += nodes.Text(f" - {of_type} ")

            t = [ref_to_class(hwIO.__class__), ]
            dt = getattr(hwIO, "_dtype", None)
            if dt is not None:
                t.append(nodes.Text(f" with dtype={dt}"))

            d = hwIO._direction
            if is_HwModule:
                d = INTF_DIRECTION.opposite(d)

            t.append(nodes.Text(f" - {d.name} "))
            if hwIO._masterDir != DIRECTION.OUT:
                t.append(nodes.Text(f"(Master={hwIO._masterDir.name}) "))

            i_p.extend(t)

            obj_list += nodes.list_item('', i_p)
            io_name_to_descr_paragraph[name] = i_p

        interfaces = hwt_io(io_name_to_descr_paragraph)
        interfaces += description_group_list

        self.state.nested_parse(self.content,
                    self.content_offset,
                    interfaces)

        return [interfaces, ]


def merge_variable_lists_into_hwt_io(app: Sphinx, domain: str, objtype: str, contentnode: nodes.Element):
    return merge_variable_lists_into_hwt_objs(app, domain, objtype, contentnode, hwt_io)


def setup(app: Sphinx):
    app.connect('object-description-transform', merge_variable_lists_into_hwt_io)
    app.add_node(hwt_io,
                 html=(hwt_io.visit_html,
                       hwt_io.depart_html))
    app.add_directive('hwt-io', HwtIODirective)
