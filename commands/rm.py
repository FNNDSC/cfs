import  click
from    prototype   import  *
from    lib         import  core
from    lib         import  file as FILE
from    pathlib     import  Path
from    pfmisc      import  Colors
from    commands    import  ls
import  shutil, os
import  pudb
from    typing      import  Generator
import  pandas      as      pd

# Instantiate a "core" object called Imp
_Rm:core.Core = core.Core

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

def file_rm(this, src:Path) -> bool:
    """
    Remove a single file <src>

    Args:
        this (_type_): prototype self
        src (path): source path (file) [cfs FS]

    Returns:
        bool: success on delete operation
    """
    srcReal:Path    = this.cfs2fs(src)
    if not srcReal.is_file():
         this.error_exit(str(src), "source file", "cfs")
    try:
        srcReal.unlink()
    except:
         return False
    return True

def file_isSymLink(file:Path, l_fileSrc:list=[]) -> bool:
    b_islink:bool   = False
    try:
        fileRefs:str    = FILE.File(file).refs
    except:
        return b_islink

    if '<-' in fileRefs:
        l_fileSrc.append(fileRefs.split('<-')[1])
        b_islink     = True
    return b_islink

def file_hasSymLinks(file:Path) -> bool:
     fileRefs:str   = FILE.File(file).refs
     return '->' in fileRefs

def file_deleteSymlinkedFile(file:Path, l_ref:list=[]) -> bool:
    # First, delete the symlink from the manifest where it exists
    df:pd.DataFrame = FILE.File(file).manifest.remove_entry('name', file.name)
    # Then, if the ref path (i.e. the source) is also passed,
    # remove mention of file from the original real source manifest
    if len(l_ref):
        ref:Path            = l_ref[0]
        fileRefs:str        = FILE.File(ref).refs
        l_refs:list[str]    = fileRefs.split(';')
        l_refs.remove(f'->{str(file)}')
        fileRefs            = ';'.join(l_refs)
        FILE.File(ref).manifest.update_entry({'refs': fileRefs}, ref.name)
    return True

def file_removeSymlinkedCopies(file:Path, l_ref:list=[]) -> int:
    count:int      = 0
    l_copies:list  = FILE.File(file).refs.replace('->', '').split(';')
    for virtcopy in l_copies:
        file_deleteSymlinkedFile(Path(virtcopy), l_ref)
        count +=  1
    return count

def file_process(this, file:Path) -> bool:
    b_success:bool          = False
    b_symbolicLink:bool     = False
    file                    = this.path_expand(file)
    df_file:pd.DataFrame    = LS.files_get(file)
    if df_file.empty:
        print(f"{file} not found... skipping.")
        return b_success

    # pudb.set_trace()

    l_symlink:list          = []
    if file_isSymLink(file, l_symlink):
        b_success = True if file_deleteSymlinkedFile(file, [Path(l_symlink[0])]) else False
        b_symbolicLink = True
    elif file_hasSymLinks(file):
        b_success = True if file_removeSymlinkedCopies(file, []) else False
    if not b_symbolicLink:
        # This is "real" file... delete it from its
        # directory manifest and remove the real from
        # from the real FS.
        FILE.File(file).manifest.remove_entry('name', file.name)
        b_success = file_rm(this, file)

    return b_success

def singleElement_generator(path:Path) -> Generator[Path, None, None]:
     yield path

def delete_do(this, src:Path, show:bool) -> int:
    count:int  = 0
    iterator:Generator[Path, None, None] = singleElement_generator(src)
    if "*" in src.name:
         iterator = src.parent.expanduser().glob(src.name)
    elif src.is_dir():
         iterator = src.iterdir()
    for child in iterator:
        # if child.is_file():
        if show:
            print(f"[rm]{str(src):50}")
        file_process(this, child)
        count += 1
    return count

# Attach those methods to our prototype
_Rm.delete_do              = delete_do


@click.command(help="""
                                delete files

This command deletes files -- depending on the actual file this might delete
only the table reference or it might also delete the real data. In the case
of real data deletion, all linked files are also removed.

""")
@click.argument('source', required = True)
@click.option('--recursive',
              is_flag = True,
              help    = 'If set, do a recursive delete [not implemented]')
@click.option('--show',
              is_flag = True,
              help    = 'If set, print the files as they are deleted')
def rm(source, show, recursive) -> int:
    # pudb.set_trace()
    Rm:_Rm              = _Rm()
    src:Path            = Path(source)
    filesDeleted:int    = Rm.delete_do(src, show)
    return filesDeleted
