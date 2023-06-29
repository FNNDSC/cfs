import  click
from    prototype   import  *
from    lib         import  core
from    lib         import  file as FILE
from    pathlib     import  Path
import  os

_mkdir:type        = core.Core

def dir_record(this, directory:Path):
    pudb.set_trace()
    parentManifest:FILE.Manifest    = FILE.Manifest(FILE.File(directory.parent))
    parentManifest.update_entry(parentManifest.create('dir'))

_mkdir.dir_record   = dir_record

@click.command(help="""
                                make directory

This command creates a new directory in the ChRIS File System space.
New directory creation entails the creation also of a "hidden" __CHRISOS
directory that contains meta file system information.

""")
@click.argument('directory', required = True)
def mkdir(directory:str) -> None:
    pudb.set_trace()
    MKDIR:_mkdir    = _mkdir()
    MKDIR.init()
    # target:Path     = Path(MKDIR.cwd()) / Path(directory)
    target:Path     = MKDIR.path_expand(Path(directory))
    realPath:Path   = MKDIR.cfs2fs(target)
    realPath.mkdir(parents = True, exist_ok = True)
    metaPath:Path   = realPath / MKDIR.core.metaDir
    metaPath.mkdir(parents = True, exist_ok = True)
    (metaPath / Path(MKDIR.meta.fileStatTable)).touch()
    (metaPath / Path(MKDIR.meta.fileMetaTable)).touch()
    MKDIR.dir_record(Path(target))
