import  click
from    prototype   import  *
from    lib         import  core, file
from    pathlib     import  Path
import  os
import  pandas      as      pd
import  pudb
from    tabulate    import  tabulate

_ls:type        = core.Core

def files_get(this, path:Path, attribs:str = "") -> pd.DataFrame:
    df_files:pd.DataFrame   = pd.DataFrame()
    manifestFile:Path       = Path('')
    file:str                = ""
    manifestFile, file      = this.manifest_get(path)
    try:
        df_files            = pd.read_csv(str(this.cfs2fs(manifestFile)))[1:]
    except:
        pass
    if file:
        df_files            = df_files[df_files['name'] == file]
    if attribs:
        l_attribs:list      = attribs.split(',')
        df_files            = df_files[l_attribs]
    return df_files

def files_print(this, df_files:pd.DataFrame, long:bool) -> bool:
    if not len(df_files):
        return False
    if long:
        print(tabulate(df_files, headers = 'keys', showindex = False, tablefmt="simple_outline"))
    else:
        print(tabulate(df_files[['name']], showindex = False))
    return True

def dirs_print(this, path:Path, long) -> None:
    # This only "lists" the directories that might exist
    # in the <path>. Could probably be improved using _fstat on
    # on the dirs themselves.
    str_item:str    = ""
    for item in Path(this.cfs2fs(path)).iterdir():
        str_item    = str(item).replace(str(this.realRoot), '', 1)
        str_item    = str_item.replace(str(this.cwd()), '', 1)
        if str_item.startswith(os.path.sep):
            str_item = str_item[1:]
        if this.core.metaDir in str_item:
            continue
        # We only print "dirs" from the real FS.
        # "files" are determined from the _f_stat file in __CHRISOS
        if item.is_dir():
            if long:
                print(f"{'dir' if item.is_dir() else 'file'} - {Path(str_item) / Path(' ') if item.is_dir() else ''}")
            else:
                print(f"{Path(str_item) / Path(' ') if item.is_dir() else ''} ", end="")


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
@click.argument('path',     required = False)
@click.option('--attribs',  required = False,
              help      = 'A comma separated list of file attributes to return/print')
@click.option('--long',
              is_flag   = True,
              help      = 'If set, use a long listing format')
def ls(path:str, attribs:str, long) -> None:
    # pudb.set_trace()
    LS:_ls  = _ls()
    LS.init()
    if path:
        path   = LS.path_expand(Path(path))
    else:
        path   = LS.cwd()
    if LS.cfs2fs(path).is_dir():
        dirs_print(LS, Path(path), long)
    files_print(LS, files_get(LS, Path(path), attribs), long)
    print("")


