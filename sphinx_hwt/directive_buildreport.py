from posixpath import dirname
from shutil import copyfile
from os import path, makedirs
from docutils import nodes
from typing import Optional
from docutils.parsers.rst import Directive
from sphinx.util import logging
from sphinx.application import Sphinx
from sphinx.locale import _
from hwt.synthesizer.interface import Interface
from hwt.synthesizer.unit import Unit
from sphinx_hwt.utils import get_absolute_name_of_class_of_node, \
    hwt_objs, merge_variable_lists_into_hwt_objs, get_constructor_name, \
    get_instance_from_directive_node, construct_property_description_list, \
    ref_to_class, construct_hwt_obj
from sphinx_hwt.directive_schematic import SchematicLink, SchematicPaths
import sqlite3


class BuildReportPath:

    SQLICON_PATH = path.join(path.dirname(__file__), "html", "sql.png")

    def DB_PATH(buildreport_database_name):
        return path.join(path.dirname(__file__), "html", buildreport_database_name)
        #path.join(path.dirname(__file__), "..", "tests", "test_buildReport_simple", buildreport_database_name)

    @classmethod
    def get_sql_icon_name_absolute(cls, document):
        return path.join(document.settings.env.app.builder.outdir, cls.get_static_path(document), "sql.png")

    @classmethod
    def get_db_name_absolute(cls, document, buildreport_database_name):
        return path.join(document.settings.env.app.builder.outdir, cls.get_static_path(document), buildreport_database_name)

    @classmethod
    def get_static_path(cls, document):
        static_paths = document.settings.env.config.html_static_path
        if not static_paths:
            return "_static"
        return static_paths[0]


class HwtBuildReportTableDirective(Directive):
    def __init__(self, name, arguments, options, content,
                 lineno, content_offset, block_text, state, state_machine, table_header, table_data):
        self.table_header = table_header
        self.table_data = table_data
        super().__init__(name, arguments, options, content, lineno,
                         content_offset, block_text, state, state_machine)

    def generate_table_name(self):
        name = self.name
        fieldname = nodes.field_name(_(name), _(name))
        icon_dst = BuildReportPath.get_sql_icon_name_absolute(
            self.state.document)

        makedirs(dirname(icon_dst), exist_ok=True)
        copyfile(BuildReportPath.SQLICON_PATH, icon_dst)

        config = HwtBuildreportDirective.config_file(self)
        db_dst = BuildReportPath.get_db_name_absolute(
            self.state.document, config.hwt_buildreport_database_name)

        makedirs(dirname(db_dst), exist_ok=True)
        copyfile(BuildReportPath.DB_PATH(
            config.hwt_buildreport_database_name), db_dst)

        img = nodes.image(uri="/_static/sql.png", height="24px",
                          width="24px", alt="Not Found")

        db_link_element = nodes.reference("",  # internal=False,
                                          refuri=db_dst)
        db_link_element.append(img)
        fieldname += db_link_element
        return fieldname

    def generate_table_body(self):
        header = self.table_header
        colwidths = tuple(1 for x in header)

        table = nodes.table()
        tgroup = nodes.tgroup(cols=len(header))
        table += tgroup

        for colwidth in colwidths:
            tgroup += nodes.colspec(colwidth=colwidth)
        thead = nodes.thead()
        tgroup += thead
        thead += self.create_table_row(header)

        tbody = nodes.tbody()
        tgroup += tbody

        for data_row in self.table_data:
            tbody += self.create_table_row(data_row)
        return table

    def run(self):
        table_list = nodes.definition_list()
        obj_desc = nodes.field()
        table_list += obj_desc

        obj_desc += self.generate_table_name()
        obj_desc += self.generate_table_body()

        return [table_list]

    @classmethod
    def create_table_row(cls, row_cells):
        row = nodes.row()
        for cell in row_cells:
            entry = nodes.entry()
            row += entry
            entry += nodes.paragraph(text=cell)
        return row


class HwtBuildreportDirective(Directive):
    optional_arguments = 1
    final_argument_whitespace = False
    has_content = False

    def config_file(self):
        config = self.state.document.settings.env.config
        return config

    def register_in_db(self, component_class_path: str, constructor_name: Optional[str]):
        """
        :param component_class_path: class path
        :param constructor_name: aditional name of the function which can configure the component
        """
        config = self.config_file()
        sqlconnect = sqlite3.connect(config.hwt_buildreport_database_name)
        sqlcursor = sqlconnect.cursor()

        sqltable = "CREATE TABLE IF NOT EXISTS builds (component_class_path text, constructor_name text)"
        sqlcursor.execute(sqltable)

        sqlquerry = 'INSERT INTO builds VALUES (?, ?);'
        sqlcursor.execute(sqlquerry, (component_class_path, constructor_name))

        sqlconnect.commit()
        sqlconnect.close()

    def run(self):

        node = self.state
        component_class_path = get_absolute_name_of_class_of_node(node)
        constructor_fn_name = get_constructor_name(self)
        config = self.config_file()

        self.register_in_db(component_class_path, constructor_fn_name)
        sqlconnect = sqlite3.connect(config.hwt_buildreport_database_name)
        sqlcursor = sqlconnect.cursor()

        tables = config.hwt_buildreport_tables

        build_reports = []
        for (table_name, table_header) in tables:
            sqlcursor.execute(
                ''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name=? ''', (table_name, ))

            if sqlcursor.fetchone()[0] == 0:
                continue

            table_header_str = ", ".join(table_header)
            sqlcursor.execute(
                f"SELECT {table_header_str:s} FROM {table_name:s} WHERE component_name=?", (component_class_path, ))
            table_data = sqlcursor.fetchall()
            build_report = HwtBuildReportTableDirective(
                table_name, self.arguments,
                self.options, self.content,
                self.lineno, self.content_offset,
                self.block_text, self.state,
                self.state_machine, table_header, table_data).run()

            if table_data:
                build_reports.extend(build_report)
            else:
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Missing record for {component_class_path:s} in {table_name:s} in {config.hwt_buildreport_database_name:s}")
                # build_report.append(nodes.Text("Empty"))

        sqlconnect.commit()
        sqlconnect.close()

        return [*build_reports, ]


def setup(app: Sphinx):
    app.add_directive('hwt-buildreport', HwtBuildreportDirective)
    app.add_config_value('hwt_buildreport_tables', [], True)
    app.add_config_value('hwt_buildreport_database_name',
                         "hwt_buildreport_database.db", True)
