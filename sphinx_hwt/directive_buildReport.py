from os import path, makedirs
from docutils import nodes
from typing import Optional
from docutils.parsers.rst import Directive
import logging
from sphinx.application import Sphinx
from sphinx.locale import _
from hwt.synthesizer.interface import Interface
from hwt.synthesizer.unit import Unit
from sphinx_hwt.utils import get_absolute_name_of_class_of_node, \
    hwt_objs, merge_variable_lists_into_hwt_objs, get_constructor_name, \
    get_instance_from_directive_node, construct_property_description_list, \
    ref_to_class, construct_hwt_obj
from sphinx_hwt.directive_schematic import SchematicLink, SchematicPaths

# TableExample, self


class TableExample(Directive):
    def __init__(self, name, arguments, options, content,
                 lineno, content_offset, block_text, state, state_machine, table_data):
        self.table_data = table_data
        super().__init__(name, arguments, options, content, lineno,
                         content_offset, block_text, state, state_machine)

    def run(self):
        name = self.name
        table_data = self.table_data

        colwidths = tuple(1 for x in table_data.keys())
        header = tuple(table_data.keys())
        data = [tuple(table_data.values()), ]

        table_list = nodes.field_list()
        obj_desc = nodes.field()
        obj_desc += nodes.field_name(_(name), _(name))
        table_list += obj_desc

        table = nodes.table()
        obj_desc += table
        tgroup = nodes.tgroup(cols=len(header))
        table += tgroup
        for colwidth in colwidths:
            tgroup += nodes.colspec(colwidth=colwidth)
        thead = nodes.thead()
        tgroup += thead
        thead += self.create_table_row(header)
        tbody = nodes.tbody()
        tgroup += tbody
        for data_row in data:
            tbody += self.create_table_row(data_row)
        return [table_list]

    @classmethod
    def create_table_row(cls, row_cells):
        row = nodes.row()
        for cell in row_cells:
            entry = nodes.entry()
            row += entry
            entry += nodes.paragraph(text=cell)
        return row


class BuildReportPaths(SchematicPaths):
    BUILD_REPORT_FILES_DIR = "buildreport"

    @classmethod
    def get_build_report_file_name_absolute(cls, document, absolute_name, serialno):
        return path.join(document.settings.env.app.builder.outdir,
                         cls.get_build_report_file_name(document, absolute_name, serialno))

    @classmethod
    def get_build_report_file_name(cls, document, absolute_name, serialno):
        sp = cls.get_static_path(document)
        return "%s-%s.%s" % (
            path.join(sp, cls.BUILD_REPORT_FILES_DIR, absolute_name),
            serialno,
            "csv")


class hwt_buildreport(nodes.General, nodes.Element):
    def __init__(self, constructor_fn_name: Optional[str], *args, **kwargs):
        """
        :param constructor_fn_name: optional name of explicit constructor function
        """
        super(hwt_buildreport, self).__init__(*args, **kwargs)
        self["constructor_fn_name"] = constructor_fn_name

    @staticmethod
    def visit_html(self, node: "hwt_buildreport"):
        absolute_name = get_absolute_name_of_class_of_node(node)
        constructor_fn_name = node["constructor_fn_name"]
        serialno = node["serialno"]

        try:
            build_report_file = BuildReportPaths.get_build_report_file_name_absolute(
                self.document, absolute_name, serialno)
            makedirs(path.dirname(build_report_file), exist_ok=True)
            u = construct_hwt_obj(
                absolute_name, constructor_fn_name, Unit, "hwt-buildreport")

            report_data = {'lut': 0, 'ff': 0, 'latch': 0,
                           'bram': 0, 'uram': 0, 'dsp': 0}
            # with ReplayingExecutor("/home/kali/Dokumenty/hwtBuildsystem/tests/SimpleUnitAxiStreamTop_synth_trace.json") as v:
            #    r = buildUnit(v, u, "tmp",
            #                  synthesize=True,
            #                  implement=False,
            #                  writeBitstream=False,
            #                  # openGui=True,
            #                  )
            #    report_data = getLutFfLatchBramUramDsp(r.parseUtilizationSynth())
            description_group_list = []

            with open(build_report_file, "w") as file:
                header = []
                valuesrow = []
                for k, v in report_data.items():
                    header.append(k)
                    valuesrow.append(str(v))

                file.write(";".join(header) + "\n")
                file.write(";".join(valuesrow) + "\n")

            csv = nodes.Text("SOMETHING")
            node += csv

        except Exception as e:
            logging.error(e, exc_info=True)
            raise Exception(
                f"Error occured while processing of {absolute_name:s}")

    @staticmethod
    def depart_html(self, node: "hwt_buildreport"):
        pass


class hwtBuildreportDirective(Directive):
    optional_arguments = 1
    final_argument_whitespace = False
    has_content = False

    def run(self):

        #build_report_list, obj_list = construct_property_description_list('HDL build reports')

        constructor_fn_name = get_constructor_name(self)
        env = self.state.document.settings.env
        serialno = env.new_serialno('hwt_buildreport')

        # build_report = hwt_buildreport(constructor_fn_name=constructor_fn_name,
        #                            serialno=serialno)
        #build_report_list += build_report
        report_data = {'lut': 0, 'ff': 0, 'latch': 0,
                       'bram': 0, 'uram': 0, 'dsp': 0}
        report_datav2 = {'SOMETHING': 120, 'HF': 0, 'LH': 50,
                         'bram': 20, 'uram': 30, 'dsp': 4}

        name = "TB1"
        build_reports = []
        for table_data in [report_data, report_datav2]:
            build_report = TableExample(name, self.arguments, self.options, self.content, self.lineno,
                                        self.content_offset, self.block_text, self.state, self.state_machine, table_data).run()
            build_reports.extend(build_report)
        # self.state.nested_parse(self.content,
        #            self.content_offset,
        #            build_report)
        return [*build_reports, ]


def setup(app: Sphinx):
    app.add_node(hwt_buildreport,
                 html=(hwt_buildreport.visit_html,
                       hwt_buildreport.depart_html))
    app.add_directive('hwt-buildreport', hwtBuildreportDirective)
