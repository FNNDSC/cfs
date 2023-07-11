import  click
from    prototype   import  *
from    lib         import  core, jobber
from    pathlib     import  Path
import  click
import  pudb
from    typing      import  Any
import  readline
import  sys
from    tabulate    import tabulate

_tree:type          = core.Core

def directories_list(this, path:Path=Path(''), negfilter:str="", mask:str="") -> list[Path]:
    """
    List all directories from this "cwd" or from optional <path>. Optionally
    remove any directories that contain a <negfilter> substring.

    Args:
        this (_type_): _description_
        path (Path, optional): Start path from which to tree. Defaults to Path('').
        negfilter (str, optional): Remove any directory names that contain <negfilter>.
                                   Defaults to "" -- string can be optionally comma
                                   separated.

    Returns:
        list[Path]: list of directory paths.
    """
    # pudb.set_trace()
    directories:list[Path]  = [p for p in path.rglob('*') if p.is_dir()]
    if mask:
        directories = [str(d).replace(mask, '') for d in directories]
    if filter:
        directories = [d for d in directories if negfilter not in str(d)]
    return directories

_tree.directories_list  = directories_list

@click.command(help="""
                                CFS tree

A somewhat idiosyncratic UNIX "tree" command that simply lists all the
directories under a given path.

""")
@click.option('--filter',
              required  = False,
              help      = 'An optional negative filter on directory substrings'
              )
@click.option('--mask',
              required  = False,
              help      = 'An optional mask to remove from the tree list strings'
              )
@click.argument('path',
                required = False)
def tree(path, filter, mask) -> None:
    # pudb.set_trace()
    TREE:_tree      = _tree()
    TREE.init()
    Core:core.Core  = core.Core()
    for dir in TREE.directories_list(Core.cfs2fs(path), str(filter), str(mask)):
        print(dir)
