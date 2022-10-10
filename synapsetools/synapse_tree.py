def get_data_folderIDs(folderID) -> list:
    """Function to get foldersIDs under the given folder
    Returns:
        list: SynapseIDs for the target folder
    """
    syn = Synapse().client()
    # get study folders
    folders = list(syn.getChildren(folderID, includeTypes=["folder"]))
    synIDs = [f["id"] for f in folders]
    return synIDs


def get_folder_tree(
    temp_dir, dirpath, clickWrap_AR: str, controlled_AR: str, dirname_mappings={}
):
    """Function to produces a depth indented listing of directory for a Synapse folder
       and attach AR info
    Args:
        temp_dir : path for temp directory
        dirpath: dirpath form synapseclient.walk
        clickWrap_AR (str): clickWrap accessRequirement ID for the given folder
        controlled_AR (str): controlled accessRequirement ID for the given folder
    Returns: temporary directory is created in the temp_dir folder
    """
    added_ar = ""
    if clickWrap_AR:
        added_ar = f"{added_ar}_CW-{str(clickWrap_AR[0])}"
    if controlled_AR and "CW" in added_ar:
        added_ar = f"{added_ar},AR-{str(controlled_AR[0])}"
    elif controlled_AR:
        added_ar = f"{added_ar}_AR-{str(controlled_AR[0])}"
    if added_ar:
        new_dirname = f"{dirpath[0]}{added_ar}"
    else:
        new_dirname = dirpath[0]
    structure = os.path.join(temp_dir, new_dirname)
    if os.path.dirname(structure) in dirname_mappings.keys():
        structure = structure.replace(
            os.path.dirname(structure), dirname_mappings[os.path.dirname(structure)]
        )
        if os.path.exists(structure):
            shutil.rmtree(structure)
        os.mkdir(structure)
        dirname_mappings[os.path.join(temp_dir, dirpath[0])] = structure
    else:
        if os.path.exists(structure):
            shutil.rmtree(structure)
        os.mkdir(structure)
        dirname_mappings[os.path.join(temp_dir, dirpath[0])] = structure

def get_accessRequirementIds(folderID: str) -> list:
    """Function to get accessRequirementId for a given folder

    Args:
        folderID (str): folder SynapseID

    Returns:
        list: clickWrap_AR and controlled_AR
    """
    syn = Synapse().client()
    # TODO: explore why this API called twice for each entity
    all_ar = syn.restGET(uri=f"/entity/{folderID}/accessRequirement")["results"]
    if all_ar:
        clickWrap_AR = [ar["id"] for ar in all_ar if not "isIDURequired" in ar.keys()]
        controlled_AR = [ar["id"] for ar in all_ar if "isIDURequired" in ar.keys()]
    else:
        clickWrap_AR = ""
        controlled_AR = ""
    return clickWrap_AR, controlled_AR

def get_AR_folders(out_dir, folderID) -> pd.DataFrame:
    """function to get datafolders with AR information and to create temporary
      folders in the out_dir to generate tree
    Args:
        out_dir (str): directory to houses the temporary folders
        folderID (str): data release folder SynapseID

    Returns: pd.DataFrame: a dataframe contains data folder name, Synapse ID, clickWrap_AR and controlled_AR
    """
    syn = Synapse().client()
    folders = pd.DataFrame()
    walkedPath = walk(syn, folderID, ["folder"])
    temp_dir = tempfile.mkdtemp(dir=out_dir)
    dirname_mappings = {}
    for dirpath, dirname, filename in walkedPath:
        folder = pd.DataFrame([dirpath], columns=["folder_name", "folder_ID"])
        # append ARs
        clickWrap_AR, controlled_AR = get_accessRequirementIds(folder.folder_ID[0])
        if clickWrap_AR:
            folder["clickWrap_AR"] = str(clickWrap_AR[0])
        if controlled_AR:
            folder["controlled_AR"] = str(controlled_AR[0])
        get_folder_tree(
                temp_dir, dirpath, clickWrap_AR, controlled_AR, dirname_mappings
            )
        folders = pd.concat([folders, folder], ignore_index=True)
    os.rename(temp_dir, os.path.join(out_dir, folderID))
    return folders

def generate_folder_tree(out_dir, filename, output_folderID):
    syn = Synapse().client()
    file = open(f"{filename}.txt", "w")
    subprocess.run(["tree", "-d", out_dir], stdout=file)
    table_out = syn.store(
        File(
            filename,
            parent=output_folderID,
        )
    )
    os.remove(f"{filename}.txt")


