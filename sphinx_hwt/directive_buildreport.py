from docutils import nodes
from docutils.parsers.rst import Directive
from os import path, makedirs
from posixpath import dirname
from shutil import copyfile
from sphinx.application import Sphinx
from sphinx.locale import _
from sphinx.util import logger
import sqlite3
from typing import Optional

from sphinx_hwt.utils import get_absolute_name_of_class_of_node, \
    get_constructor_name


class BuildreportPaths:
    """
    Container of the paths for buildreport directives
    """

    SQLICON_PATH = path.join(path.dirname(__file__), "html", "sql.png")

    @classmethod
    def get_sql_icon_name_absolute(cls, env):
        return path.join(env.srcdir,
                         cls.get_static_path_from_env(env),
                         "sql.png")

    @classmethod
    def get_static_path(cls, document):
        return cls.get_static_path_from_env(document.settings.env)

    @classmethod
    def get_static_path_from_env(cls, env):
        static_paths = env.config.html_static_path
        if not static_paths:
            return "_static"
        return static_paths[0]

    @classmethod
    def get_db_file_dst_absolute_from_env(cls, env):
        static_paths = env.config.html_static_path
        if static_paths:
            static_path = static_paths[0]
        else:
            static_path = "_static"

        return path.join(
            env.app.builder.outdir,
            static_path,
            "hwt_buildreport.db"
        )

    @classmethod
    def get_db_file_dst_absolute(cls, state):
        return cls.get_db_file_dst_absolute_from_env(state.document.settings.env)

    @classmethod
    def get_db_file_dst_uri(cls, state):
        return path.join(cls.get_static_path(state.document),
                         "hwt_buildreport.db")


def get_config(state):
    return state.document.settings.env.config


class HwtBuildReportTableDirective(Directive):
    """
    A sphinx directive which adds a single table from provided data into a document
    """

    def __init__(self, name, arguments, options, content,
                 lineno, content_offset, block_text, state, state_machine, table_header, table_data):
        self.table_header = table_header
        self.table_data = table_data
        super().__init__(name, arguments, options, content, lineno,
                         content_offset, block_text, state, state_machine)

    def generate_table_name(self):
        name = self.name
        fieldname = nodes.field_name(_(name), _(name))

        db_link_element = nodes.reference(
            "", refuri=BuildreportPaths.get_db_file_dst_uri(self.state))

        img = nodes.image(uri="/_static/sql.png", height="24px",
                          width="24px", alt="DB icon")

        db_link_element.append(img)
        fieldname += db_link_element
        return fieldname

    def generate_table_body(self):
        header = self.table_header
        colwidths = tuple(1 for _ in header)

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

    def register_in_db(self, component_class_path: str, constructor_name: Optional[str]):
        """
        Adds a record about this component into builds table in database to mark that this component should be build.

        :param component_class_path: class path
        :param constructor_name: aditional name of the function which can configure the component
        """
        sqlconnect = sqlite3.connect(
            BuildreportPaths.get_db_file_dst_absolute(self.state))
        try:
            sqlcursor = sqlconnect.cursor()

            sqltable = "CREATE TABLE IF NOT EXISTS builds (component_class_path text, constructor_name text)"
            sqlcursor.execute(sqltable)

            sqlquerry = 'INSERT INTO builds VALUES (?, ?);'
            sqlcursor.execute(
                sqlquerry, (component_class_path, constructor_name))

            sqlconnect.commit()
        finally:
            sqlconnect.close()

    def run(self):
        """
        Add the record about this component into DB to mark it for build and
        add build report tables from the data in DB if available.
        """
        state = self.state
        component_class_path = get_absolute_name_of_class_of_node(state)
        constructor_fn_name = get_constructor_name(self)

        # mark in db for later build
        self.register_in_db(component_class_path, constructor_fn_name)

        # load build report from db and construct report tables in document
        sqlconnect = sqlite3.connect(
            BuildreportPaths.get_db_file_dst_absolute(state))
        try:
            sqlcursor = sqlconnect.cursor()
            build_reports = []
            for ((table_db_buildreport_name, table_sphix_name), table_header) in get_config(state).hwt_buildreport_tables:
                sqlcursor.execute(
                    "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (table_db_buildreport_name,))

                if sqlcursor.fetchone()[0] == 0:
                    # if table does not exists
                    continue

                table_columns_to_select_str = ", ".join(table_header)
                sqlcursor.execute(
                    f"SELECT {table_columns_to_select_str:s} FROM {table_db_buildreport_name:s} WHERE component_name=?", (component_class_path,))
                table_data = sqlcursor.fetchall()
                build_report = HwtBuildReportTableDirective(
                    table_sphix_name, self.arguments,
                    self.options, self.content,
                    self.lineno, self.content_offset,
                    self.block_text, self.state,
                    self.state_machine, table_header, table_data).run()

                if table_data:
                    build_reports.extend(build_report)
                else:
                    logger.warning(
                        f"Missing record for {component_class_path:s} in {table_db_buildreport_name:s} in {self.get_db_file_src():s}")
                    build_reports.append(nodes.Text(
                        f"No build reports available in {table_db_buildreport_name:s}"))
        finally:
            sqlconnect.close()

        return [*build_reports, ]


def init_static_files_and_database(app: Sphinx, env, docnames):
    db_dst = BuildreportPaths.get_db_file_dst_absolute_from_env(env)
    makedirs(dirname(db_dst), exist_ok=True)
    import requests

    db_name: str = env.config.hwt_buildreport_database_name

    if db_name is None:
        return

    elif db_name.startswith("http://") or db_name.startswith("https://"):
        r = requests.get(db_name, allow_redirects=True)
        with open(db_dst, 'wb') as f:
            f.write(r.content)
    else:
        db_src = path.join(env.srcdir,
                           db_name)

        copyfile(db_src, db_dst)

    icon_dst = BuildreportPaths.get_sql_icon_name_absolute(env)
    makedirs(dirname(icon_dst), exist_ok=True)
    copyfile(BuildreportPaths.SQLICON_PATH, icon_dst)


def setup(app: Sphinx):
    app.add_directive('hwt-buildreport', HwtBuildreportDirective)
    app.add_config_value('hwt_buildreport_tables', [], True)
    app.add_config_value('hwt_buildreport_database_name',
                         None, True)

    app.connect('env-before-read-docs', init_static_files_and_database)
