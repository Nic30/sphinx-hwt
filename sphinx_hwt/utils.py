from docutils import nodes
from docutils.parsers.rst import Directive
import re
from sphinx.addnodes import desc_signature, pending_xref
from sphinx.application import Sphinx
from sphinx.locale import _
from sphinx.util import typing
from typing import Union, List, Dict

RE_IS_ID = re.compile("\w+")


# http://www.sphinx-doc.org/en/stable/extdev/index.html#dev-extensions
def generic_import(name: Union[str, List[str]]):
    """
    Import using string or list of module names
    """
    if isinstance(name, str):
        components = name.split('.')
    else:
        assert isinstance(name, list), name
        components = name

    mod = None
    for i, comp in enumerate(components):
        try:
            # if imported sucessfully __import__ returns a top module
            mod = __import__('.'.join(components[:i + 1]))
        except ModuleNotFoundError:
            for comp in components[1:]:
                try:
                    mod = getattr(mod, comp)
                except AttributeError:
                    raise
    return mod


def get_absolute_name_of_class_of_node(node):
    """
    Get a module path for an object from its node in doc.
    """
    parentClsNode = node.parent.parent
    assert parentClsNode.attributes['objtype'] == 'class', \
        (parentClsNode.attributes['objtype'], parentClsNode)
    assert parentClsNode.attributes['domain'] == 'py', \
        parentClsNode.attributes['domain']
    sign = node.parent.parent.children[0]
    assert isinstance(sign, desc_signature)
    absolute_name = sign.attributes['ids'][0]
    return absolute_name


class hwt_objs(nodes.General, nodes.Element):
    """
    A directive which adds a list of HDL defined interfaces for Unit instances
    The message also contains information about default value and type of the parameter.

    :ivar obj_list: format (name, type_str, value_str)
    """

    def __init__(self, obj_name_to_descr_paragraph: Dict[str, nodes.Element], rawsource='', *children, **attributes):
        super(hwt_objs, self).__init__(rawsource, *children, **attributes)
        self["obj_name_to_descr_paragraph"] = obj_name_to_descr_paragraph


def get_constructor_name(directive: Directive):
    """
    Get a first argument of the directive and check if it is a function.
    """
    if directive.arguments:
        assert len(directive.arguments) == 1, directive.arguments
        constructor_fn_name = directive.arguments[0]
        constructor_fn_name = constructor_fn_name.strip()
        assert len(constructor_fn_name) >= 0
        assert RE_IS_ID.match(constructor_fn_name), constructor_fn_name
        return constructor_fn_name
    else:
        return None


def construct_hwt_obj(absolute_name: str, constructor_fn_name: str, allowed_classes, debug_directive_name: str):
    if constructor_fn_name is None:
        unitCls = generic_import(absolute_name)
        if not issubclass(unitCls, allowed_classes):
            raise AssertionError(
                f"Can not use {debug_directive_name:s} sphinx directive"
                f" for {absolute_name:s} because it is not subclass of {allowed_classes}")
        u = unitCls()
    else:
        assert len(constructor_fn_name) > 0 and RE_IS_ID.match(constructor_fn_name), constructor_fn_name
        _absolute_name = []
        assert ".." not in absolute_name, absolute_name
        for n in absolute_name.split(sep=".")[:-1]:
            if n != "":
                _absolute_name.append(n)
        _absolute_name.append(constructor_fn_name)

        constructor_fn = generic_import(_absolute_name)
        u = constructor_fn()
        if not isinstance(u, allowed_classes):
            raise AssertionError(
                f"Can not use {debug_directive_name:s} sphinx directive"
                f" with {_absolute_name:s} because function did not returned instance of {allowed_classes}, (returned {u} of class {u.__class__})")

    return u


def get_instance_from_directive_node(directive: Directive, allowed_classes):
    '''
    Converts

    .. code-block:: text

        .. directive:
        .. directive: constructor_fn_name

    to instance, if constructor_fn_name is not specified the current class instantiated.
    '''

    node = directive.state
    debug_directive_name = directive.__class__.__name__
    constructor_fn_name = get_constructor_name(directive)
    absolute_name = get_absolute_name_of_class_of_node(node)
    return construct_hwt_obj(absolute_name, constructor_fn_name, allowed_classes, debug_directive_name)


def merge_variable_lists_into_hwt_objs(app: Sphinx, domain: str, objtype: str, contentnode: nodes.Element, hwt_objs_cls) -> None:
    """
    Move doc from variable lists in class documentation to HDL param list if the variable is a HDL Param instance.
    """
    if domain != 'py':
        return
    if app.config.autodoc_typehints != 'signature':
        return
    if objtype == 'class' and app.config.autoclass_content not in ('class',):
        return

    hwt_objs_list = [n for n in contentnode if isinstance(n, hwt_objs_cls)]
    field_lists = [n for n in contentnode if isinstance(n, nodes.field_list)]
    if hwt_objs_list and field_lists:
        if len(hwt_objs_list) > 1:
            raise NotImplementedError(hwt_objs_list)
        for fl in field_lists:
            merge_field_lists_to_hdl_objs(fl, hwt_objs_list[0])


def merge_field_lists_to_hdl_objs(field_list: nodes.field_list, hwt_obj_list: hwt_objs):
    obj_name_to_descr_paragraph = hwt_obj_list["obj_name_to_descr_paragraph"]
    to_remove = []
    for field in list(field_list):
        field_name = field[0].astext()
        parts = re.split(' +', field_name)
        if parts[0] == 'ivar':
            if len(parts) == 2:
                # :ivar xxx:
                name = parts[1]
                doc_paragraph = obj_name_to_descr_paragraph.get(name, None)
                if doc_paragraph is None:
                    continue  # regular variable (not HDL obj instance)
                # children of the paragraph with the doc
                doc_paragraph += field[1][0].children

            elif len(parts) > 2:
                # :ivar xxx yyy:
                name = ' '.join(parts[2:])
                doc_paragraph = obj_name_to_descr_paragraph.get(name, None)
                if doc_paragraph is None:
                    continue  # regular variable (not HDL obj instance)
                # children of the paragraph with the doc
                doc_paragraph += field[1][0].children

            else:
                raise NotImplementedError("Unknon format of ivar", parts)

        elif parts[0] == 'type':
            name = parts[1]
            doc_paragraph = obj_name_to_descr_paragraph.get(name, None)
            if doc_paragraph is None:
                continue  # regular variable (not HDL obj instance)
            # children of the paragraph with the doc
            doc_paragraph += field[1][0].children

        to_remove.append(field)

    for field in to_remove:
        field.replace_self([])


def construct_property_description_list(name):
    """
    Construct a skeleton for sphinx member description block
    """
    description_group_list = nodes.field_list()
    obj_desc = nodes.field()
    obj_desc += nodes.field_name(_(name), _(name))
    description_group_list += obj_desc

    obj_list = nodes.bullet_list()
    description_group_list += nodes.field_body('', obj_list)
    return description_group_list, obj_list


def ref_to_class(class_obj):
    """
    Create the sphinx pending_xref for a class
    """
    class_path = typing.stringify(class_obj)
    t_ref = pending_xref(refdomain='py', reftype='class', reftarget=class_path)
    t_ref += nodes.Text(class_path)
    return t_ref

