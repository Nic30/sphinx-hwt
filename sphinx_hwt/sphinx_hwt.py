import json
from os import path, makedirs
import re
from shutil import copytree, rmtree
from sphinx.addnodes import desc_signature
from sphinx.locale import _
from typing import Optional

from docutils import nodes
from docutils.parsers.rst import Directive
from hwt.synthesizer.dummyPlatform import DummyPlatform
from hwt.synthesizer.unit import Unit
from hwtGraph.elk.containers.idStore import ElkIdStore
from hwtGraph.elk.fromHwt.convertor import UnitToLNode
from hwtGraph.elk.fromHwt.defauts import DEFAULT_PLATFORM, \
    DEFAULT_LAYOUT_OPTIMIZATIONS
import logging

# http://www.sphinx-doc.org/en/stable/extdev/index.html#dev-extensions

def synthesised(u: Unit, targetPlatform=DummyPlatform()):
    assert not u._wasSynthetised()
    u._loadDeclarations()

    for _ in u._toRtl(targetPlatform):
        pass
    return u


def generic_import(name):
    if isinstance(name, str):
        components = name.split('.')
    else:
        assert isinstance(name, list), name
        components = name

    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)

    return mod


class SchematicPaths():
    SCHEMATIC_VIEWER_URL = "schematic_viewer/schematic_viewer.html"
    SCHEMATIC_DIR_PREFIX = "../../"  # relative path from SCHEMATIC_VIEWER_URL
    SCHEMATIC_FILES_DIR = "hwt_schematics"  # path relative to static dir
    SCHEMATIC_FILES_EXTENSION = "json"
    SCHEMATIC_VIEWER_SRC_DIR = path.join(path.dirname(__file__), "html")

    @classmethod
    def get_sch_file_name_absolute(cls, document, absolute_name, serialno):
        return path.join(document.settings.env.app.builder.outdir,
                         cls.get_sch_file_name(document, absolute_name, serialno))

    @classmethod
    def get_static_path(cls, document):
        static_paths = document.settings.env.config.html_static_path
        return static_paths[0]

    @classmethod
    def get_sch_file_name(cls, document, absolute_name, serialno):
        sp = cls.get_static_path(document)
        return "%s-%s.%s" % (
            path.join(sp, cls.SCHEMATIC_FILES_DIR, absolute_name),
            serialno,
            cls.SCHEMATIC_FILES_EXTENSION)

    @classmethod
    def get_sch_viewer_link(cls, document):
        return path.join(cls.get_static_path(document),
                         cls.SCHEMATIC_VIEWER_URL)

    @classmethod
    def get_sch_viewer_dir(cls, document):
        return path.join(document.settings.env.app.builder.outdir,
                         SchematicPaths.get_static_path(document),
                         "schematic_viewer")


RE_IS_ID = re.compile("\w+")


class SchematicLink(nodes.General, nodes.Inline, nodes.TextElement):

    def __init__(self, constructor_fn: Optional[str]=None, *args, **kwargs):
        """
        :param constructor_fn: optional name of explicit constructor function
        """
        super(SchematicLink, self).__init__(*args, **kwargs)
        self["constructor_fn "] = constructor_fn 

    @staticmethod
    def visit_html(self, node):
        """
        Generate html elements and schematic json
        """
        parentClsNode = node.parent.parent
        assert parentClsNode.attributes['objtype'] == 'class'
        assert parentClsNode.attributes['domain'] == 'py'
        sign = node.parent.parent.children[0]
        assert isinstance(sign, desc_signature)
        absolute_name = sign.attributes['ids'][0]
        _construct = node["constructor_fn "] 
        serialno = node["serialno"]

        try:
            if _construct is None:
                unitCls = generic_import(absolute_name)
                if not issubclass(unitCls, Unit):
                    raise AssertionError(
                        "Can not use hwt-schematic sphinx directive and create schematic"
                        " for %s because it is not subclass of %r" % (absolute_name, Unit))
                u = unitCls()
            else:
                assert len(_construct) > 0 and RE_IS_ID.match(_construct), _construct
                _absolute_name = []
                assert ".." not in absolute_name, absolute_name
                for n in  absolute_name.split(sep=".")[:-1]:
                    if n != "":
                        _absolute_name.append(n)
                _absolute_name.append(_construct)
                
                constructor_fn = generic_import(_absolute_name)
                u = constructor_fn()
                if not isinstance(u, Unit):
                    raise AssertionError(
                        "Can not use hwt-schematic sphinx directive and create schematic"
                        " for %s because function did not returned instance of %r, (%r)" % (
                            _absolute_name, Unit, u))

            schem_file = SchematicPaths.get_sch_file_name_absolute(
                self.document, absolute_name, serialno)
            makedirs(path.dirname(schem_file), exist_ok=True)

            with open(schem_file, "w") as f:
                synthesised(u, DEFAULT_PLATFORM)
                g = UnitToLNode(u, optimizations=DEFAULT_LAYOUT_OPTIMIZATIONS)
                idStore = ElkIdStore()
                data = g.toElkJson(idStore)
                json.dump(data, f)

            viewer = SchematicPaths.get_sch_viewer_link(self.document)
            sch_name = SchematicPaths.get_sch_file_name(
                self.document, absolute_name, serialno)
            ref = nodes.reference(text=_("schematic"),  # internal=False,
                                  refuri="%s?schematic=%s" % (
                                      viewer,
                                      path.join(SchematicPaths.SCHEMATIC_DIR_PREFIX,
                                                sch_name)))
            node += ref
        except Exception as e:
            logging.error(e, exc_info=True)
            raise Exception(
                "Error  occured while processing of %s" % absolute_name)

    @staticmethod
    def depart_html(self, node):
        pass


class HwtSchematicDirective(Directive):
    optional_arguments = 1
    final_argument_whitespace = False
    has_content = False

    def __init__(self, *args, **kwargs):
        Directive.__init__(self, *args, **kwargs)
        self._extra_static_files_initialized_for = set()

    def copy_extra_static_files(self):
        document = self.state.document
        sp = SchematicPaths.get_static_path(document)
        if sp not in self._extra_static_files_initialized_for:
            viewer_dir = SchematicPaths.get_sch_viewer_dir(document)
            if path.exists(viewer_dir):
                rmtree(viewer_dir)

            copytree(SchematicPaths.SCHEMATIC_VIEWER_SRC_DIR, viewer_dir)
            self._extra_static_files_initialized_for.add(sp)

    def run(self):
        # build dir path
        # https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/sphinxext/plot_directive.py#L699
        # targetid = "hwt-schematic-%d" % env.new_serialno('hwt-schematic')
        # targetnode = nodes.target('', '', ids=[targetid])
        self.copy_extra_static_files()
        constructor_fn = None
        if self.arguments:
            assert len(self.arguments) == 1, self.arguments
            constructor_fn = self.arguments[0]
            constructor_fn = constructor_fn.strip()
            assert len(constructor_fn) >= 0
            assert RE_IS_ID.match(constructor_fn), constructor_fn
        
        env = self.state.document.settings.env
        serialno = env.new_serialno('SchematicLink')
        schema_node = SchematicLink(constructor_fn=constructor_fn,
                                    serialno=serialno)

        self.state.nested_parse(self.content,
                                self.content_offset,
                                schema_node)

        return [schema_node, ]


def setup(app):
    app.add_node(SchematicLink,
                 html=(SchematicLink.visit_html,
                       SchematicLink.depart_html))
    app.add_directive('hwt-schematic', HwtSchematicDirective)
