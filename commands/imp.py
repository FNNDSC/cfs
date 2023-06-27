import  click
from    prototype   import *
from    lib         import core, file
from    pathlib     import Path
from    pfmisc      import Colors
import  shutil, os
import  pudb

_imp:type        = core.Core

def badpath_errorExit(this, path:str, type:str, fs:str="") -> None:
        message:str =                                                           \
            Colors.LIGHT_RED + f"\n\n\t\t\tDanger, Will Robinson!\n\n" +        \
            Colors.NO_COLOUR + f"The {type}\n\n\t " +                           \
            Colors.YELLOW    + path +                                           \
            Colors.NO_COLOUR + f"\n\nwas not found on the {fs} filesystem.\n" + \
                               f"Please make sure the {type} really exists."
        this.stderr(message, 2)

def destination_resolve(this, path:Path) -> Path:
    """
    Resolve the destination path. Two possibilities exist:

    * destination is a directory (so must already exist)
    * destination is a file (so might not need to already exist)

    Args:
        this (_type_): this object
        path (Path): the destination path (either a dir or file)

    Returns:
        Path: cfs path
    """
    # pudb.set_trace()
    path = this.path_expand(path)
    if not this.dir_checkExists(path):
          # In this case, we assume that the path ends in the file
          # name. Correspondingly, check that the parent directory
          # exists
          if not this.dir_checkExists(path.parent):
               this.error_exit(str(path.parent), "ChRIS dir", "cfs")
    return path

def file_copy(this, src:Path, dest:Path) -> Path:
    """
    Copy a single file from <src> to <dest>, returning
    <dest> or empty path on fail

    Args:
        this (_type_): prototype self
        src (path): source path (file) [real FS]
        dest (path): destination path (file) [cfs FS]

    Returns:
        Path: destination path (file) or empty path on fail
    """
    if not src.is_file():
         this.error_exit(str(src), "source file", "real")
    destReal:Path           = this.cfs2fs(dest)
    shutil.copy(src, destReal)
    return destReal

def file_process(this, src:Path, dest:Path) -> bool:
    pudb.set_trace()
    if src.name != dest.name:
         dest  = dest / src.name
    fileObj:type    = file.File(this.fs2cfs(this.file_copy(src, dest)))
    manifest:type   = file.Manifest(fileObj)
    manifest.update_entry()

    return True

_imp.error_exit             = badpath_errorExit
_imp.destination_resolve    = destination_resolve
_imp.file_copy              = file_copy
_imp.file_process           = file_process

@click.command(help="""
                                import files

This command simulates the "import"/creation of actual new files / data
in the ChRIS File System. The <sourcefile> is a "real file system" file
and the <targetfile> is a ChRIS File System file.

This method updates the file meta information in the target directory to
which the file is uploaded.

""")
@click.argument('sourcefile', required = True)
@click.argument('targetfile', required = True)
@click.option('--recursive',
              is_flag = True,
              help    = 'If set, do a recursive copy')
def imp(sourcefile, targetfile, recursive) -> bool:
#    pudb.set_trace()
    imp:_imp        = _imp()
    imp.init()
    src:Path        = Path(sourcefile)
    dest:Path       = imp.destination_resolve(Path(targetfile))
    fileOK:bool     = imp.file_process(src, dest) if src.is_file() else False
    return fileOK

    # if recursive:
    #     print(f'Performing a recursive copy...')
    # else:
    #     print(f'Performing a single copy...')
