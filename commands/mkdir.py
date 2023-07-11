import  click
from    prototype   import  *
from    lib         import  core
from    lib         import  file as FILE
from    pathlib     import  Path
import  os
from    typing      import  Union, Any, Literal

_mkdir:type        = core.Core

def dir_manifestsUpdate(this, directory:Path) -> tuple[type | bool, FILE.Manifest]:
    # Create/update the manifest in the child dir
    childManifest:Union[FILE.Manifest, bool]    = dir_manifestGet(this, directory)

    # Update the manifest in the parent directory
    parentManifest:Union[FILE.Manifest, bool]   = dir_manifestGet(this, directory.parent)
    parentManifest.update_entry(FILE.metaData_set(
                                    parentManifest.metaFields,
                                    parentManifest.create('dir'),
                                    name = directory.name))

    return childManifest, parentManifest

def dir_manifestGet(this, path:Path) -> Union[FILE.Manifest, bool]:
    metaPath:Path   = path / this.core.metaDir
    if not this.cfs2fs(metaPath).is_dir():
        return False

    statFile:Path           = metaPath / Path(this.meta.fileStatTable)
    manifest:FILE.Manifest  = FILE.Manifest(FILE.File(statFile))
    return manifest

def subpaths_get(target:Path) -> list[Path]:
    """
    Simply return a list of subpaths starting one
    directory level deep (i.e. skipping '/')

    Args:
        target (Path): the target path

    Returns:
        list[Path]: a list of increasingly deep subpaths
    """
    subpathlist:list[Path]  = list(target.parents)
    subpathlist.reverse()
    subpathlist.append(target)
    return subpathlist[1:]

_mkdir.manifestsUpdate  = dir_manifestsUpdate
_mkdir.manifestGet      = dir_manifestGet

@click.command(help="""
                                make directory

This command creates a new directory in the ChRIS File System space.
New directory creation entails the creation also of a "hidden" __CHRISOS
directory that contains meta file system information.

""")
@click.argument('directory', required = True)
def mkdir(directory:str) -> None:
    # pudb.set_trace()
    MKDIR:_mkdir            = _mkdir()
    MKDIR.init()
    target:Path             = MKDIR.path_expand(Path(directory))

    for subpath in subpaths_get(target):
        # Create the actual directory, and add the meta files/dir
        realPath:Path   = MKDIR.cfs2fs(subpath)
        metaPath:Path   = realPath / MKDIR.core.metaDir
        realPath.mkdir(parents = True, exist_ok = True)     # Actual dir
        metaPath.mkdir(parents = True, exist_ok = True)     # Meta dir
        (metaPath / Path(MKDIR.meta.fileStatTable)).touch() # stat table
        (metaPath / Path(MKDIR.meta.fileMetaTable)).touch() # meta table
        # And now record this directory in the meta file table of its
        # parent
        MKDIR.manifestsUpdate(Path(subpath))
