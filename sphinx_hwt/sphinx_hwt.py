from docutils import nodes
from docutils.parsers.rst import Directive
import json
from os import path, makedirs
from shutil import copytree, rmtree
from sphinx.addnodes import desc_signature
from sphinx.locale import _

from hwt.synthesizer.dummyPlatform import DummyPlatform
from hwt.synthesizer.unit import Unit
from hwtGraph.elk.containers.idStore import ElkIdStore
from hwtGraph.elk.fromHwt.convertor import UnitToLNode
from hwtGraph.elk.fromHwt.defauts import DEFAULT_PLATFORM, \
    DEFAULT_LAYOUT_OPTIMIZATIONS
from typing import Optional


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
    SCHEMATIC_FILES_EXTENSION = ".json"
    SCHEMATIC_VIEWER_SRC_DIR = path.join(path.dirname(__file__), "html")

    @classmethod
    def get_sch_file_name_absolute(cls, document, absolute_name):
        return path.join(document.settings.env.app.builder.outdir,
                         cls.get_sch_file_name(document, absolute_name))

    @classmethod
    def get_static_path(cls, document):
        static_paths = document.settings.env.config.html_static_path
        return static_paths[0]

    @classmethod
    def get_sch_file_name(cls, document, absolute_name):
        sp = cls.get_static_path(document)
        return path.join(sp, cls.SCHEMATIC_FILES_DIR, absolute_name) \
            + cls.SCHEMATIC_FILES_EXTENSION

    @classmethod
    def get_sch_viewer_link(cls, document):
        return path.join(cls.get_static_path(document),
                         cls.SCHEMATIC_VIEWER_URL)

    @classmethod
    def get_sch_viewer_dir(cls, document):
        return path.join(document.settings.env.app.builder.outdir,
                         SchematicPaths.get_static_path(document),
                         "schematic_viewer")


class SchematicLink(nodes.TextElement):

    def __init__(self, constructor_fn: Optional[str]=None, *args, **kwargs):
        """
        :param constructor_fn: optional name of explicit constructor function
        """
        super(SchematicLink, self).__init__(*args, **kwargs)
        self._constructor_fn = constructor_fn

    @staticmethod
    def visit_html(self, node):
        parentClsNode = node.parent.parent
        assert parentClsNode.attributes['objtype'] == 'class'
        assert parentClsNode.attributes['domain'] == 'py'
        sign = node.parent.parent.children[0]
        assert isinstance(sign, desc_signature)
        absolute_name = sign.attributes['ids'][0]
        if node._constructor_fn is None:
            unitCls = generic_import(absolute_name)
            if not issubclass(unitCls, Unit):
                raise AssertionError(
                    "Can not use hwt-schematic sphinx directive and create schematic"
                    " for %s because it is not subclass of %r" % (absolute_name, Unit))
            u = unitCls()
        else:
            _absolute_name = absolute_name.split(sep=".")[:-1]
            _absolute_name.append(node._constructor_fn)
            constructor_fn = generic_import(_absolute_name)
            u = constructor_fn()
            if not isinstance(u, Unit):
                raise AssertionError(
                    "Can not use hwt-schematic sphinx directive and create schematic"
                    " for %s because function did not returned instance of %r, (%r)" % (
                        _absolute_name, Unit, u))

        schem_file = SchematicPaths.get_sch_file_name_absolute(
            self.document, absolute_name)
        makedirs(path.dirname(schem_file), exist_ok=True)

        with open(schem_file, "w") as f:
            synthesised(u, DEFAULT_PLATFORM)
            g = UnitToLNode(u, optimizations=DEFAULT_LAYOUT_OPTIMIZATIONS)
            idStore = ElkIdStore()
            data = g.toElkJson(idStore)
            json.dump(data, f)

        viewer = SchematicPaths.get_sch_viewer_link(self.document)
        sch_name = SchematicPaths.get_sch_file_name(
            self.document, absolute_name)
        ref = nodes.reference(text=_("schematic"),  # internal=False,
                              refuri="%s?schematic=%s" % (
                                  viewer,
                                  path.join(SchematicPaths.SCHEMATIC_DIR_PREFIX,
                                            sch_name)))
        node += ref
        self.visit_admonition(node)

    @staticmethod
    def depart_html(self, node):
        self.depart_admonition(node)


class HwtSchematicDirective(Directive):
    required_arguments = 0
    optional_arguments = 1
    has_content = True
    option_spec = {}

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
            constructor_fn = self.arguments[0]

        schema_node = SchematicLink(constructor_fn=constructor_fn)
        # schema_node += nodes.title(_('Schematic'), _('Todo'))
        self.state.nested_parse(self.content,
                                self.content_offset,
                                schema_node)

        return [schema_node, ]


def setup(app):
    app.add_node(SchematicLink,
                 html=(SchematicLink.visit_html,
                       SchematicLink.depart_html))
    app.add_directive('hwt-schematic', HwtSchematicDirective)
