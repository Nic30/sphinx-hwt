import json
import os
from shutil import copytree

from hwt.hwModule import HwModule
from hwtGraph.elk.containers.idStore import ElkIdStore
from hwtGraph.elk.fromHwt.convertor import HwModuleToLNode
from hwtGraph.elk.fromHwt.defauts import DEFAULT_LAYOUT_OPTIMIZATIONS
from sphinx_hwt.directive_schematic import SchematicPaths


def hwt_HwModule_to_html(synthetizedHwModule: HwModule, filePath:str, optimizations=DEFAULT_LAYOUT_OPTIMIZATIONS):
    dirPath = os.path.dirname(filePath)
    g = HwModuleToLNode(synthetizedHwModule, optimizations=optimizations)
    idStore = ElkIdStore()
    data = g.toElkJson(idStore)
    with open(os.path.join(SchematicPaths.SCHEMATIC_VIEWER_SRC_DIR, "schematic_viewer.html")) as templateFile:
        template = templateFile.read()
    graphJson = json.dumps(data)
    assert "// {END_OF_JS}" in template
    template = template.replace("// {END_OF_JS}", f"var graph = {graphJson:s};\n    hwSchematic.bindData(graph);")
    with open(filePath, "w") as f:
        f.write(template)
    copytree(os.path.join(SchematicPaths.SCHEMATIC_VIEWER_SRC_DIR, "node_modules"),
             os.path.join(dirPath, "node_modules"), dirs_exist_ok=True)
