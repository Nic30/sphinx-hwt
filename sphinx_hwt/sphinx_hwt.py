from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives import flag, unchanged
from docutils import nodes
from docutils.parsers.rst.states import Body
from sphinx.locale import _


class SchematicLink(nodes.Admonition, nodes.Element):

    @staticmethod
    def depart_html(self, node):
        self.depart_admonition(node)

    @staticmethod
    def visit_html(self, node):
        self.visit_admonition(node)


class HwtSchematicDirective(Directive):
    required_arguments = 0
    optional_arguments = 0
    has_content = True
    option_spec = dict(module=unchanged, func=unchanged, ref=unchanged,
                       prog=unchanged, path=unchanged, nodefault=flag,
                       nodefaultconst=flag, filename=unchanged,
                       manpage=unchanged, nosubcommands=unchanged, passparser=flag,
                       noepilog=unchanged, nodescription=unchanged,
                       markdown=flag, markdownhelp=flag)
    def run(self):
        env = self.state.document.settings.env
        # docName = env.docname.
        # document.attributes['source']
        #objName = 
        
        # build dir path
        # https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/sphinxext/plot_directive.py#L699
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
