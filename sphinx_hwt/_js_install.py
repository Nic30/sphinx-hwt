import os
from subprocess import check_call
import sys
from shutil import copyfile

TOP_DIR = os.getcwd()

JS_FILES = [
    "node_modules/d3/dist/d3.js",
    "node_modules/d3-hwschematic/dist/d3-hwschematic.js",
    "node_modules/d3-hwschematic/src/elk/elk-worker.js"]


def npm_installation_check():
    try:
        check_call(["npm", "--version"])
    except Exception:
        print("Can not find npm, which is required for the installation", file=sys.stderr)
        sys.exit(1)


def run_npm_install():
    my_env = os.environ.copy()
    # PYTHONPATH has to be removed because webworker-threads (d3-hwschematic -> elk -> )
    # has install time dependency on python2 and PYTHONPATH 
    # overrideds python2 import paths
    if "PYTHONPATH" in my_env:
        del my_env["PYTHONPATH"]
    origCwd = os.getcwd()
    try:
        os.chdir(TOP_DIR)
        check_call(["npm", "install"], env=my_env)
    finally:
        os.chdir(origCwd)


def find_extra_js_files_in_npm(dirname):
    """
    Download npm packages required by package.json and extract required
    files from them
    """
    if dirname == "":
        if not os.path.exists(os.path.join(TOP_DIR, "node_modules")):
            npm_installation_check()
            run_npm_install()

        for js in JS_FILES:
            downloaded_js_name = os.path.join(TOP_DIR, js)
            assert os.path.exists(downloaded_js_name), downloaded_js_name
            installed_js_name = os.path.join("sphinx_hwt", "html", js)
            os.makedirs(os.path.dirname(installed_js_name), exist_ok=True)
            copyfile(downloaded_js_name, installed_js_name)
            yield installed_js_name  
