import  click
from    prototype   import  *
from    lib         import  core
from    pathlib     import  Path
import  os

_mkdir:type        = core.Core

@click.command(help="""
                                make directory

This command creates a new directory in the ChRIS File System space.
New directory creation entails the creation also of a "hidden" __CHRISOS
directory that contains meta file system information.

""")
@click.argument('directory', required = True)
def mkdir(directory:str) -> None:
    # pudb.set_trace()
    MKDIR:_mkdir    = _mkdir()
    MKDIR.init()
    target:Path     = Path(MKDIR.cwd()) / Path(directory)
    realPath:Path   = MKDIR.cfs2fs(target)
    realPath.mkdir(parents = True, exist_ok = True)
    metaPath:Path   = realPath / MKDIR.core.metaDir
    metaPath.mkdir(parents = True, exist_ok = True)
    (metaPath / Path(MKDIR.meta.fileStatTable)).touch()
    (metaPath / Path(MKDIR.meta.fileMetaTable)).touch()
