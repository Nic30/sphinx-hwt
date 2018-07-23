from docutils import nodes
from docutils.parsers.rst import Directive
from os import path, makedirs
from sphinx.addnodes import desc_signature
from sphinx.locale import _
from hwt.synthesizer.unit import Unit
from hwtLib.tests.synthesizer.interfaceLevel.subunitsSynthesisTC import synthesised
from hwtGraph.elk.fromHwt.defauts import DEFAULT_PLATFORM,\
    DEFAULT_LAYOUT_OPTIMIZATIONS
from hwtGraph.elk.fromHwt.convertor import UnitToLNode
from hwtGraph.elk.containers.idStore import ElkIdStore
import json


def generic_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)

    return mod


class SchematicLink(nodes.TextElement):
    SCHEMATIC_VIEWER_URL = "viewer.html"
    SCHEME_FILES_DIR = "hwt_schematics"  # path relative to static dir
    SCHEME_FILES_EXTENSION = ".json"

    @classmethod
    def get_sch_file_name_absolute(cls, document, absolute_name):
        return path.join(document.settings.env.app.builder.outdir,
                         cls.get_sch_file_name(document, absolute_name))

    @classmethod
    def get_sch_file_name(cls, document, absolute_name):
        static_paths = document.settings.env.config.html_static_path
        return path.join(static_paths[0], cls.SCHEME_FILES_DIR, absolute_name) \
            + cls.SCHEME_FILES_EXTENSION

    @staticmethod
    def depart_html(self, node):
        self.depart_admonition(node)

    @staticmethod
    def visit_html(self, node):

        parentClsNode = node.parent.parent
        assert parentClsNode.attributes['objtype'] == 'class'
        assert parentClsNode.attributes['domain'] == 'py'
        sign = node.parent.parent.children[0]
        assert isinstance(sign, desc_signature)
        absolute_name = sign.attributes['ids'][0]
        unitCls = generic_import(absolute_name)
        if not issubclass(unitCls, Unit):
            raise AssertionError(
                "Can not use hwt-schematic sphinx directive and create scheme"
                " for %s because it is not subclass of %r" % (absolute_name, Unit))

        schem_file = SchematicLink.get_sch_file_name_absolute(
            self.document, absolute_name)
        makedirs(path.dirname(schem_file), exist_ok=True)

        with open(schem_file, "w") as f:
            u = unitCls()
            synthesised(u, DEFAULT_PLATFORM)
            g = UnitToLNode(u, optimizations=DEFAULT_LAYOUT_OPTIMIZATIONS)
            idStore = ElkIdStore()
            data = g.toElkJson(idStore)
            json.dump(data, f)

        ref = nodes.reference(text=_("schematic"),  # internal=False,
                              refuri=SchematicLink.get_sch_file_name(
                                  self.document, absolute_name))
        node += ref
        self.visit_admonition(node)


class HwtSchematicDirective(Directive):
    required_arguments = 0
    optional_arguments = 0
    has_content = True
    option_spec = {}

    def run(self):
        env = self.state.document.settings.env

        # build dir path
        # https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/sphinxext/plot_directive.py#L699
        # targetid = "hwt-schematic-%d" % env.new_serialno('hwt-schematic')
        # targetnode = nodes.target('', '', ids=[targetid])

        schema_node = SchematicLink()
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
