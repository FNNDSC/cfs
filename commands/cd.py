import  click
from    prototype   import  *
from    lib         import  core
from    pathlib     import  Path

_cd:type        = core.Core

@click.command(help="""
                                change directory

This command changes the current working directory in a ChRIS File System. If
a directory is not specified, then assume the user home directory.

""")
@click.argument('directory', required = False)
@click.option('--echo',
              is_flag=True,
              help='If set, echo the directory to stdout')
@click.option('--echoReal',
              is_flag=True,
              help='If set, echo the _real_ directory to stdout')
def cd(directory:str, echo, echoreal) -> None:
    # pudb.set_trace()
    CD:_cd      = _cd()
    CD.init()
    if not directory:
        directory = CD.core.homeDir
    dir:Path    = Path(directory)
    dir         = CD.path_expand(dir)
    if CD.dir_checkExists(Path(dir)):
        CD.cwdWrite(dir)
    if echo or echoreal:
        print(CD.pwd_prompt(realDir = echoreal))

