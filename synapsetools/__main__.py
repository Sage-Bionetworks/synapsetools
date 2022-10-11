# import modules
import argparse
import json
import logging
import os
import shutil
import subprocess
import tempfile
from functools import partial

import pandas as pd
import synapseclient
from synapseclient import File, Table
from synapseclient.core.exceptions import (SynapseAuthenticationError,
                                           SynapseNoCredentialsError)
from synapseutils import walk

from . import synapse_tree, utils


def synapse_tree_cli(args):
    """create synapse tree cli"""
    # get the list of folders 
    folderIDs = synapse_tree.get_data_folderIDs(args.folderID)
    #create a temporary directory under the current working directory
    out_dir = tempfile.mkdtemp(dir = os. getcwd())
    get_AR_folders_temp = partial(synapse_tree.get_AR_folders, out_dir)
    results = map(get_AR_folders_temp, folderIDs)
    AR_folders = pd.concat(results)
    # update folder tree and remove temporary directory once done
    synapse_tree.generate_folder_tree(out_dir, args.filename, args.output_folderID)

def build_parser():
    """Set up argument parser and returns"""
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        title="commands",
        description="The following commands are available:",
        help='For additional help: "synapsetools <COMMAND> -h"',
    )
    parser_synapse_tree = subparsers.add_parser(
        "synapse_tree", help="Produce a depth indented listing of directory for a Synapse folder and attach AR info"
    )
    parser_synapse_tree.add_argument(
        "folderID",
        metavar="folderID",
        type=str,
        help="Synapse ID of the target folder for which you want to create a folder tree.",
    )
    parser_synapse_tree.add_argument(
        "filename",
        metavar="filename",
        type=str,
        help="Output file name. The default output file is txt file.",
    )
    parser_synapse_tree.add_argument(
        "output_folderID",
        metavar="output_folderID",
        type=str,
        help="Synapse ID of folder to save the output file.",
    )

    parser_synapse_tree.set_defaults(func=synapse_tree_cli)

    return parser

def main():
    """Invoke"""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
