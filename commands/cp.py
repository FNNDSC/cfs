import  click
from    prototype   import *
from    lib         import core
from    commands    import imp

_cp:type        = core.Core

@click.command(help="""
                                copy files

This command "copies" files from one part of ChRIS storage to another. It is
more akin to a "symbolic" link in standard UNIX file systems since data is
not actually duplicated. Rather, meta-data is stored in the hidden _fstat
file of the __CHRISOS folder in a given directory.

""")
@click.option('--recursive',
              is_flag=True,
              help='If set, do a recursive copy')
def cp(recursive) -> None:
    pudb.set_trace()
    CP:_cp  = _cp()
    CP.init()
    if recursive:
        print(f'Performing a recursive copy...')
    else:
        print(f'Performing a single copy...')
