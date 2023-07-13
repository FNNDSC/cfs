import  click
from    prototype   import  *
from    lib         import  core, file
from    pathlib     import  Path
from    pfmisc      import  Colors
from    commands    import  ls
import  shutil, os
import  pudb
from    typing      import  Generator
import  pandas      as      pd

@constructor
def Exp(this) -> None:
    this.recursive:bool     = None
    this.show:bool          = None

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

def file_pull(this, src:Path, dest:Path) -> Path:
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
    # Need to check if import will "overwrite" virtual existing
    # file
    if src.name != dest.name:
         dest  = dest / src.name
    df_dest:pd.DataFrame    = LS.files_get(dest)
    if not df_dest.empty:
         print(f"{dest} exists... skipping.")
    fileObj:type    = file.File(this.fs2cfs(this.file_copy(src, dest)))
    manifest:type   = file.Manifest(fileObj)
    manifest.update_entry({}, "", ['refs'])

    return True

def singleElement_generator(path:Path) -> Generator[Path, None, None]:
     yield path

def export_do(this, src:Path, dest:Path, show:bool) -> int:
    count:int  = 0
    iterator:Generator[Path, None, None] = singleElement_generator(src)
    if "*" in src.name:
         iterator = src.parent.expanduser().glob(src.name)
    elif src.is_dir():
         iterator = src.iterdir()
    for child in iterator:
        if child.is_file():
            if show:
                print(f"[EXT]{str(src):50} -> [CFS]{dest}")
            file_process(this, child, dest)
            count += 1
    return count

# Attach those methods to our prototype
Exp.destination_resolve     = destination_resolve
Exp.file_pull               = file_pull
Exp.file_process            = file_process
Exp.export_do               = export_do

# exp:Exp                     = Exp()
# exp.__proto__               = core.Core

@click.command(help="""
                                export files

This command simulates the "export" of files from the ChRIS File System
to a "real" file system.

""")
@click.argument('sourcefile', required = True)
@click.argument('targetfile', required = True)
@click.option('--recursive',
              is_flag = True,
              help    = 'If set, do a recursive copy')
@click.option('--show',
              is_flag = True,
              help    = 'If set, print the files as they are imported')
def exp(sourcefile, targetfile, recursive, show) -> int:
    pudb.set_trace()
    exp:Exp             = Exp()
    exp.__proto__       = core.Core
    src:Path            = Path(sourcefile)
    dest:Path           = exp.destination_resolve(Path(targetfile))
    filesExported:int   = exp.export_do(src, dest, show)
    return filesExported
