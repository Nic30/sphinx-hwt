import re
from typing import Union, List, Optional, Dict
from sphinx.addnodes import desc_signature
from hwt.synthesizer.unit import Unit
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx
from docutils import nodes

RE_IS_ID = re.compile("\w+")


# http://www.sphinx-doc.org/en/stable/extdev/index.html#dev-extensions
def generic_import(name: Union[str, List[str]]):
    if isinstance(name, str):
        components = name.split('.')
    else:
        assert isinstance(name, list), name
        components = name

    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)

    return mod


def get_absolute_name_of_class_of_node(node):
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
    A directive which adds a list of HDL defined interfaces for Unit innstances
    The message also contains information about default value and type of the parameter.
    """

    def __init__(self, obj_list: list, extra_param_doc: Optional[Dict[str, List[nodes.Element]]]=None, rawsource='', *children, **attributes):
        if extra_param_doc is None:
            extra_param_doc = {}
        self.extra_doc = extra_param_doc
        self.obj_list = obj_list
        super(hwt_objs, self).__init__(rawsource, *children, **attributes)


def get_instance_from_directive_node(directive: Directive, allowed_classes):
    '''
    Converts

    .. code-block:: Python
        """
        .. directive:
        .. directive: constructor_fn_name
        """

    to instance, if constructor_fn_name is not specified the current class instantiated.
    '''

    node = directive.state
    constructor_fn_name = None
    if directive.arguments:
        assert len(directive.arguments) == 1, directive.arguments
        constructor_fn_name = directive.arguments[0]
        constructor_fn_name = constructor_fn_name.strip()
        assert len(constructor_fn_name) >= 0
        assert RE_IS_ID.match(constructor_fn_name), constructor_fn_name

    debug_directive_name = directive.__class__.__name__
    absolute_name = get_absolute_name_of_class_of_node(node)
    if constructor_fn_name is None:
        unitCls = generic_import(absolute_name)
        if not issubclass(unitCls, allowed_classes):
            raise AssertionError(
                "Can not use %s sphinx directive"
                " for %s because it is not subclass of %r" % (debug_directive_name, absolute_name, allowed_classes))
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
                "Can not use %s sphinx directive"
                " with %s because function did not returned instance of %r, (returned %r)" % (debug_directive_name,
                    _absolute_name, allowed_classes, u))

    return u


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
    obj_names = set(hwt_obj_list.obj_get_name(p) for p in hwt_obj_list.obj_list)
    extra_doc = hwt_obj_list.extra_doc
    to_remove = []
    for field in list(field_list):
        field_name = field[0].astext()
        parts = re.split(' +', field_name)
        if parts[0] == 'ivar':
            if len(parts) == 2:
                # :ivar xxx:
                name = parts[1]
                if name not in obj_names:
                    continue  # regular variable (not HDL Param instance)
                extra = extra_doc.setdefault(name, [])
                # children of the paragraph with the doc
                extra += field[1][0].children

            elif len(parts) > 2:
                # :ivar xxx yyy:
                name = ' '.join(parts[2:])
                if name not in obj_names:
                    continue  # regular variable (not HDL Param instance)
                extra = extra_doc.setdefault(name, [])
                # children of the paragraph with the doc
                extra += field[1][0].children

            else:
                raise NotImplementedError("Unknon format of ivar", parts)

        elif parts[0] == 'type':
            name = parts[1]
            if name not in obj_names:
                continue  # regular variable (not HDL Param instance)
            extra = extra_doc.setdefault(name, [])
            # children of the paragraph with the doc
            extra += field[1][0].children

        to_remove.append(field)

    for field in to_remove:
        field.replace_self([])
