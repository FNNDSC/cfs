import  click
from    prototype   import  *
from    lib         import  core, file
from    pathlib     import  Path
import  os
import  pandas      as      pd
import  pudb
from    tabulate    import  tabulate
from    typing      import  Callable, Pattern
import  fnmatch
import  re

_ls:type        = core.Core
LS:_ls  = _ls()
LS.init()

def wildcards_check(target:Path) -> tuple[Path, str]:
    wildcard:str    = ''
    if '*' in target.name:
        wildcard    = target.name
        target      = target.parent
    return target, wildcard

def files_get(this, path:Path, **kwargs) -> pd.DataFrame:
    # pudb.set_trace()
    attribs:str             = ""
    onObjectStorage:bool    = False
    filter:str              = ""
    df_files:pd.DataFrame   = pd.DataFrame()
    manifestFile:Path       = Path('')
    file:str                = ""

    for k,v in kwargs.items():
        if k == 'attribs'           :   attribs         = v
        if k == 'onObjectStorage'   :   onObjectStorage = v

    path, filter            = wildcards_check(path)
    manifestFile, file      = this.manifest_get(path, onObjectStorage)
    realfs:Callable         = this.cfs2fs
    if onObjectStorage:
        realfs              = this.cfs2ofs
    try:
        df_files            = pd.read_csv(str(realfs(manifestFile)))
    except:
        pass
    if file:
        df_files            = df_files[df_files['name'] == file]
    if filter:
        regex_pattern:str   = fnmatch.translate(filter)
        df_files            = df_files[df_files['name'].str.\
                                contains(regex_pattern, na = False, regex = True)]
    if attribs:
        l_attribs:list      = attribs.split(',')
        df_files            = df_files[l_attribs]
    return df_files

def files_print(this, df_files:pd.DataFrame, long:bool) -> bool:
    if df_files.empty:
        return False
    if 'type' in df_files.columns and 'name' in df_files.columns:
        df_sorted:pd.DataFrame = df_files.sort_values(['type', 'name'])
    else:
        df_sorted:pd.DataFrame = df_files
    if not len(df_files):
        return False
    if long:
        print(tabulate(df_sorted, headers = 'keys', showindex = False, tablefmt="simple_outline"))
    else:
        df_sorted['name'] = df_sorted.apply(
            lambda row: row['name'] + '/' if row['type'] == 'dir' else row['name'], axis=1)
        print(tabulate(df_sorted[['name']], showindex = False, tablefmt = "plain"))
    return True

def path_checkAndExpand(path:str) -> Path:
    pathChecked:Path    = Path('')
    if path:
        pathChecked     = LS.path_expand(Path(path))
    else:
        pathChecked     = LS.cwd()
    return pathChecked

_ls.files_get       = files_get

@click.command(help="""
                                list files

This command lists the objects (files and directories) that are at a given
path. This path can be a directory, in which case possibly multiple objects
are listed, or it can be a single file in which case information about that
single file is listed.

In CFS, directories are "real". Files are "real" once -- which means a file's
bits and bytes do exist in a directory. However, CUBE uses manifests (special
hidden tables) to track file information and *not* the actual information in
the storage medium. This means that _copies_ of files to other CUBE locations
only updates the file manifest table in the target directory. The file is not
actually copied (thus not duplicated). So, one could "ls" in a given CUBE
directory where no files really exist, and still get a complete listing. In
such a case CUBE is returning the file references as if they were real actual
files.

""")
@click.argument('path',
                required = False)
@click.option('--onobjectstorage',
              is_flag   = True,
              help      = 'If set, perform operation on objectStorage')
@click.option('--attribs',  required = False,
              help      = 'A comma separated list of file attributes to return/print')
@click.option('--long',
              is_flag   = True,
              help      = 'If set, use a long listing format')
def ls(path:str, attribs:str, long, onobjectstorage) -> None:
    # pudb.set_trace()
    target:Path     = Path('')
    if path:
        target = Path(path)
    files_print(LS,
                files_get(LS, target,
                              attribs           = attribs,
                              onObjectStorage   = onobjectstorage),
                long)
    print("")


