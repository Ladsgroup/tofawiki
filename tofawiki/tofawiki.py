"""
This script provides access to a set of utilities for tofawiki

* dev_server_translation -- Starts a development webserver on localhost

Usage:
    tofawiki (-h | --help)
    tofawiki <utility> [-h | --help]

Options:
    -h | --help  Shows this documentation
    <utility>    The name of the utility to run
"""
import sys
import traceback
from importlib import import_module


USAGE = """Usage:
    tofawiki (-h | --help)
    tofawiki <utility> [-h | --help]\n"""


def main():

    if len(sys.argv) < 2:
        sys.stderr.write(USAGE)
        sys.exit(1)
    elif sys.argv[1] in ("-h", "--help"):
        sys.stderr.write(__doc__ + "\n")
        sys.exit(1)
    elif sys.argv[1][:1] == "-":
        sys.stderr.write(USAGE)
        sys.exit(1)

    module_name = sys.argv[1]
    try:
        module = import_module(".utilities." + module_name,
                               package="tofawiki")
    except ImportError:
        sys.stderr.write(traceback.format_exc())
        sys.stderr.write("Could not find utility {0}.\n".format(module_name))
        sys.exit(1)

    module.main(sys.argv[2:])

