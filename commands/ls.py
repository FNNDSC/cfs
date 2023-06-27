import  click
from    prototype   import  *
from    lib         import  core, file
from    pathlib     import  Path
import  os
import  pandas      as      pd
import  pudb
from    tabulate    import  tabulate

_ls:type        = core.Core

def files_list(this, directory:Path) -> pd.DataFrame:
    # pudb.set_trace()
    df_files:pd.DataFrame   = pd.DataFrame()
    manifestFile:Path       = directory / this.core.metaDir / this.meta.fileStatTable
    if not this.cfs2fs(manifestFile).is_file():
        return df_files
    try:
        df_files            = pd.read_csv(str(this.cfs2fs(manifestFile)))[1:]
    except:
        pass
    return df_files

def files_print(this, df_files:pd.DataFrame, long:bool) -> bool:
    if not len(df_files):
        return False
    if long:
        print(tabulate(df_files, headers = 'keys', showindex = False, tablefmt="simple_outline"))
    else:
        print(tabulate(df_files[['name']], showindex = False))
    return True

_ls.files_list       = files_list

@click.command(help="""
                                list files

This command lists files that "seem to exist" in a given directory of
ChRIS storage. The "seem to exist" is critical, since this command
returns both actual files that might physically in the directory, as
well as all files "linked" into that directory.

""")
@click.argument('directory', required = False)
@click.option('--long',
              is_flag=True,
              help='If set, use a long listing format')
@click.option('--pwd',
              is_flag=True,
              help='If set, print the current directory')
def ls(directory:str, long, pwd) -> None:
    # pudb.set_trace()
    LS:_ls  = _ls()
    LS.init()
    str_item:str    = ""
    if directory:
        directory   = LS.path_expand(Path(directory))
    else:
        directory   = LS.cwd()
    if pwd:
        print(LS.pwd_prompt())
    for item in Path(LS.cfs2fs(directory)).iterdir():
        str_item    = str(item).replace(str(LS.realRoot), '', 1)
        str_item    = str_item.replace(str(LS.cwd()), '', 1)
        if str_item.startswith(os.path.sep):
            str_item = str_item[1:]
        if LS.core.metaDir in str_item:
            continue
        # We only print "dirs" from the real FS.
        # "files" are determined from the _f_stat file in __CHRISOS
        if item.is_dir():
            if long:
                print(f"{'dir' if item.is_dir() else 'file'} - {Path(str_item) / Path(' ') if item.is_dir() else ''}")
            else:
                print(f"{Path(str_item) / Path(' ') if item.is_dir() else ''} ", end="")
    files_print(LS, files_list(LS, Path(directory)), long)
    print("")


