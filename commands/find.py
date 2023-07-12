import  click
from    prototype   import  *
from    lib         import  core, jobber
from    lib         import  file as FILE
from    pathlib     import  Path
from    pfmisc      import  Colors
from    commands    import  ls
import  shutil, os
import  pudb
from    typing      import  Generator, Any
import  pandas      as      pd
from    commands    import  mkdir, cp

# Instantiate a "core" object called Find
_Find:core.Core = core.Core

_ls:type        = ls._ls
LS:_ls          = _ls()

# Define some methods!
def badpath_errorExit(this, path:str, type:str, fs:str="") -> None:
        message:str =                                                           \
            Colors.LIGHT_RED + f"\n\n\t\t\tDanger, Will Robinson!\n\n" +        \
            Colors.NO_COLOUR + f"The {type}\n\n\t " +                           \
            Colors.YELLOW    + path +                                           \
            Colors.NO_COLOUR + f"\n\nwas not found on the {fs} filesystem.\n" + \
                               f"Please make sure the {type} really exists."
        this.stderr(message, 2)

def file_rm(this, src:Path, onobjectstorage:bool = False) -> bool:
    """
    Remove a single file <src>

    Args:
        this (_type_): prototype self
        src (path): source path (file) [cfs FS]

    Returns:
        bool: success on delete operation
    """
    srcReal:Path    = Path('')
    if onobjectstorage:
        srcReal     = this.cfs2ofs(src)
    else:
        srcReal     = this.cfs2fs(src)
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
    # pudb.set_trace()
    if len(l_ref):
        ref:Path            = l_ref[0]
        fileRefs:str        = FILE.File(*FILE.sourcePartition_resolve(ref)).refs
        l_refs:list[str]    = fileRefs.split(';')
        l_refs.remove(f'->{str(file)}')
        fileRefs            = ';'.join(l_refs)
        FILE.File(*FILE.sourcePartition_resolve(ref)).manifest.update_entry({'refs': fileRefs}, ref.name)
    return True

def file_removeSymlinkedCopies(file:Path, l_ref:list=[]) -> int:
    count:int      = 0
    l_copies:list  = FILE.File(file).refs.replace('->', '').split(';')
    for virtcopy in l_copies:
        file_deleteSymlinkedFile(Path(virtcopy), l_ref)
        count +=  1
    return count

def file_process(this, file:Path, onobjectstorage=False) -> bool:
    b_success:bool          = False
    b_symbolicLink:bool     = False
    file                    = this.path_expand(file)
    df_file:pd.DataFrame    = LS.files_get(file, attribs = "", onObjectStorage = onobjectstorage)
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
        FILE.File(file, onobjectstorage).manifest.remove_entry('name', file.name)
        b_success = file_rm(this, file)

    return b_success

def singleElement_generator(path:Path) -> Generator[Path, None, None]:
     yield path

def df_generator(df:pd.DataFrame) -> Generator[pd.Series, Any, None]:
    for _, row in df.iterrows():
        yield row

def wildcards_check(path:Path) -> tuple[Path, str]:
    wildcard:str    = ''
    if '*' in path.name:
        wildcard    = path.name
        path        = path.parent
    return path, wildcard

def source_resolve(src:Path) -> Path:
    wildcard:str            = ""
    base:Path               = Path('')
    base, wildcard          = wildcards_check(src)
    if wildcard:
        src                 = base
    else:
        src                 = base.parent
    return src

def dirlist_resolve(this, d_run:dict[Any, Any]) -> list[Path]:
    dirlist:list[Path]      = d_run['stdout'].split('\n')
    realroot:str            = str(this.dbRoot)
    dirlist                 = [(str(d).replace(realroot, '')).replace(str(Path(this.core.metaDir) / Path(this.meta.fileStatTable)), '') for d in dirlist[:-1]]
    dirlist                 = [d[:-1] if d.endswith('/') else d for d in dirlist]
    dirlist                 = [Path(d) for d in dirlist]
    return dirlist

def do(this, search:str, saveto:str, show:bool, onobjectstorage:bool) -> int:
    pudb.set_trace()
    count:int               = 0
    system                  = jobber.Jobber({'verbosity': 0, 'noJobLogging': True})
    command:str             = f"rg -l {search} {this.dbRoot}"
    d_run:dict[Any, Any]    = system.job_run(command)
    savedir:str             = f"{this.core.homeDir}/searches/{saveto}"
    searchlist:list         = this.dirlist_resolve((d_run))
    if searchlist:
        system.job_run(f"cfs mkdir {savedir}")
    for dir in searchlist:
        source:str          = f"{dir}/*{search}"
        command             = f"cfs cp {source} {savedir}"
        print(command)
    return count

# Attach those methods to our prototype
_Find.do                = do
_Find.dirlist_resolve   = dirlist_resolve


@click.command(help="""
                                find files

This command finds files.

""")
@click.argument('search',   required = True)
@click.argument('saveto',     required = True)
@click.option('--onobjectstorage',
              is_flag   = True,
              help      = 'If set, perform operation on objectStorage')
@click.option('--show',
              is_flag = True,
              help    = 'If set, print the files as they are found')
def find(search, saveto, show, onobjectstorage) -> int:
    pudb.set_trace
    Find:_Find          = _Find()
    filesFound:int      = Find.do(search, saveto, show, onobjectstorage)
    return filesFound
