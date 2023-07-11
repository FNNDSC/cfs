import  click
from    prototype   import  *
from    lib         import  core, file
from    pathlib     import  Path
from    pfmisc      import  Colors
from    commands    import  ls, cp
import  shutil, os
import  pudb
from    typing      import  Generator
import  pandas      as      pd
import  uuid

# Instantiate a "core" object called Imp
_Imp:core.Core = core.Core

LS:ls._ls    = ls._ls()

# Define some methods!
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

def file_import(this, src:Path, dest:Path) -> Path:
    """
    Copy a single file from (external/real) <src> to
    object storage. Name the file with a UUID prefix
    in storage.

    In the "root" of the db use a "file tracking" table
    to associate the storage object with a location <dest>
    in the directory-first db.

    Args:
        this (_type_): prototype self
        src (path): source path (file) [real FS]
        dest (path): destination path (file) [cfs FS]

    Returns:
        Path: real import path
    """
    if not src.is_file():
         this.error_exit(str(src), "source file", "real")

    # Copy into objectStore
    objectStoreFile:Path    = Path(f'{uuid.uuid1()}-{str(src.name)}')
    shutil.copy(src, this.objRoot / objectStoreFile)

    objectStoreFile         = Path('/') / objectStoreFile

    # Now create an entry for this file in the object store
    # manifest
    # pudb.set_trace()
    useObjectStoragePartition:bool = True
    file.File(objectStoreFile, useObjectStoragePartition).manifest.update_entry({}, "", ['refs'])

    return objectStoreFile

def file_process(this, src:Path, dest:Path) -> bool:
    # Need to check if import will "overwrite" virtual existing
    # file
    if src.name != dest.name:
         dest  = dest / src.name
    df_dest:pd.DataFrame    = LS.files_get(dest)

    if not df_dest.empty:
         print(f"{dest} exists... skipping.")
         return False

    # Now do a reference (aka "hard link") from the object storage to the
    # db manifest in the destination directory / key-table.
    fromObjectStorage:bool  = True
    CP:cp._Cp = cp._Cp()
    CP.copy(file_import(this, src, dest), dest, fromObjectStorage)

    return True

def singleElement_generator(path:Path) -> Generator[Path, None, None]:
     yield path

def import_do(this, src:Path, dest:Path, show:bool) -> int:
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
_Imp.error_exit             = badpath_errorExit
_Imp.destination_resolve    = destination_resolve
_Imp.file_import            = file_import
_Imp.file_process           = file_process
_Imp.import_do              = import_do


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
@click.option('--show',
              is_flag = True,
              help    = 'If set, print the files as they are imported')
def imp(sourcefile, targetfile, recursive, show) -> int:
    # pudb.set_trace()
    Imp:_Imp            = _Imp()
    src:Path            = Path(sourcefile)
    dest:Path           = Imp.destination_resolve(Path(targetfile))
    filesImported:int   = Imp.import_do(src, dest, show)
    return filesImported
