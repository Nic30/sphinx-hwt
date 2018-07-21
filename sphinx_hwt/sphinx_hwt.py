from docutils import nodes
from docutils.parsers.rst import Directive
from os import path
from sphinx.addnodes import desc_signature
from sphinx.locale import _
from hwt.synthesizer.unit import Unit

def generic_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)

    return mod

class SchematicLink(nodes.TextElement):
    SCHEMATIC_VIEWER_URL = "viewer.html"
    SCHEME_FILES_DIR = "_downloads/"
    SCHEME_FILES_EXTENSION = ".json"
    
    @classmethod
    def get_sch_file_name(cls, absolute_name):
        return path.join(cls.SCHEME_FILES_DIR, absolute_name) + cls.SCHEME_FILES_EXTENSION
    
    @classmethod
    def get_sch_link(cls, sch_file_name):
        return "%s&%s" % (cls.SCHEMATIC_VIEWER_URL, sch_file_name)

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
        
        ref = nodes.reference(text=_("schematic"),  # internal=False,
                              refuri=self.get_sch_link(absolute_name))
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
