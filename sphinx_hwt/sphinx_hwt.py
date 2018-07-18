from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx.locale import _


class SchematicLink(nodes.Admonition, nodes.Element):

    @staticmethod
    def depart_html(self, node):
        self.depart_admonition(node)

    @staticmethod
    def visit_html(self, node):
        self.visit_admonition(node)


class HwtSchematicDirective(Directive):

    def run(self):
        env = self.state.document.settings.env

        targetid = "todo-%d" % env.new_serialno('todo')
        targetnode = nodes.target('', '', ids=[targetid])

        todo_node = SchematicLink('\n'.join(self.content))
        # todo_node += nodes.title(_('Todo'), _('Todo'))
        self.state.nested_parse(self.content,
                                self.content_offset,
                                todo_node)

        return [targetnode, todo_node]


def setup(app):
    app.add_node(SchematicLink,
                 html=(SchematicLink.visit_html,
                       SchematicLink.depart_html))
    app.add_directive('hwt-schematic', HwtSchematicDirective)
