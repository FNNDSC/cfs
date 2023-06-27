import  click
from    prototype   import  *
from    lib         import  core
from    pathlib     import  Path

_pwd:type        = core.Core


@click.command(help="""
                        print working directory

Simply print the current working directory in the ChRIS File System.

""")
@click.option('--real',
              is_flag   = True,
              help      = 'If set, print the "real" directory, i.e. on real FS')
def pwd(real) -> None:
    # pudb.set_trace()
    PWD:_pwd  = _pwd()
    PWD.init()
    if not real:
        print(PWD.cwdRead())
    else:
        print(PWD.cfs2fs(PWD.cwdRead()))
