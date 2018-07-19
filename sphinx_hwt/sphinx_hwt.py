from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx.locale import _
from sphinx.addnodes import desc_signature


class SchematicLink(nodes.TextElement):

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
        absoluteName = sign.attributes['ids'][0]
        ref = nodes.reference(text="schematic", internal=False,
                              refuri="viewer.html&%s.json" % absoluteName)
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
        targetid = "hwt-schematic-%d" % env.new_serialno('hwt-schematic')
        targetnode = nodes.target('', '', ids=[targetid])

        schema_node = SchematicLink()
        # schema_node += nodes.title(_('Schematic'), _('Todo'))
        self.state.nested_parse(self.content,
                                self.content_offset,
                                schema_node)

        return [targetnode, schema_node]


def setup(app):
    app.add_node(SchematicLink,
                 html=(SchematicLink.visit_html,
                       SchematicLink.depart_html))
    app.add_directive('hwt-schematic', HwtSchematicDirective)
