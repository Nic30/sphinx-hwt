from docutils import nodes
from docutils.parsers.rst import Directive
import json
import logging
from os import path, makedirs
from shutil import copytree, rmtree
from sphinx.application import Sphinx
from sphinx.locale import _
from typing import Optional

from hwt.synthesizer.unit import Unit
from hwt.synthesizer.utils import synthesised
from hwtGraph.elk.containers.idStore import ElkIdStore
from hwtGraph.elk.fromHwt.convertor import UnitToLNode
from hwtGraph.elk.fromHwt.defauts import DEFAULT_PLATFORM, \
    DEFAULT_LAYOUT_OPTIMIZATIONS
from sphinx_hwt.utils import get_absolute_name_of_class_of_node, \
    get_constructor_name, construct_hwt_obj


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
        if not static_paths:
            return "_static"
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


class SchematicLink(nodes.General, nodes.Inline, nodes.TextElement):

    def __init__(self, constructor_fn_name: Optional[str], *args, **kwargs):
        """
        :param constructor_fn_name: optional name of explicit constructor function
        """
        super(SchematicLink, self).__init__(*args, **kwargs)
        self["constructor_fn_name"] = constructor_fn_name

    @staticmethod
    def visit_html(self, node):
        """
        Generate html elements and schematic json
        """
        absolute_name = get_absolute_name_of_class_of_node(node)
        constructor_fn_name = node["constructor_fn_name"]
        serialno = node["serialno"]

        try:
            schem_file = SchematicPaths.get_sch_file_name_absolute(
                self.document, absolute_name, serialno)
            makedirs(path.dirname(schem_file), exist_ok=True)
            u = construct_hwt_obj(absolute_name, constructor_fn_name, Unit, "hwt-schematic")
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
                f"Error occured while processing of {absolute_name:s}")

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
        self.copy_extra_static_files()
        constructor_fn_name = get_constructor_name(self)
        env = self.state.document.settings.env
        serialno = env.new_serialno('SchematicLink')
        schema_node = SchematicLink(constructor_fn_name=constructor_fn_name,
                                    serialno=serialno)

        self.state.nested_parse(self.content,
                                self.content_offset,
                                schema_node)

        return [schema_node, ]


def setup(app: Sphinx):
    app.add_node(SchematicLink,
                 html=(SchematicLink.visit_html,
                       SchematicLink.depart_html))
    app.add_directive('hwt-schematic', HwtSchematicDirective)

