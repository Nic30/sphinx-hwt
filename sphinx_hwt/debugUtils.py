import json
import os
from shutil import copytree

from hwt.synthesizer.unit import Unit
from hwtGraph.elk.containers.idStore import ElkIdStore
from hwtGraph.elk.fromHwt.convertor import UnitToLNode
from hwtGraph.elk.fromHwt.defauts import DEFAULT_LAYOUT_OPTIMIZATIONS
from sphinx_hwt.directive_schematic import SchematicPaths


def hwt_unit_to_html(synthetizedUnit: Unit, filePath:str, optimizations=DEFAULT_LAYOUT_OPTIMIZATIONS):
    dirPath = os.path.dirname(filePath)
    g = UnitToLNode(synthetizedUnit, optimizations=optimizations)
    idStore = ElkIdStore()
    data = g.toElkJson(idStore)
    with open(os.path.join(SchematicPaths.SCHEMATIC_VIEWER_SRC_DIR, "schematic_viewer.html")) as templateFile:
        template = templateFile.read()
    graphJson = json.dumps(data)
    template = template.replace("// {END_OF_JS}", f"var graph = {graphJson:s};\n    hwSchematic.bindData(graph);")
    with open(filePath, "w") as f:
        f.write(template)
    copytree(os.path.join(SchematicPaths.SCHEMATIC_VIEWER_SRC_DIR, "node_modules"),
             os.path.join(dirPath, "node_modules"), dirs_exist_ok=True)
