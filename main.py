__version__ = '0.9.9'

import  pudb

import  click

from commands import (
    cp, cd, pwd, ls, mkdir, imp, rm, shell, tree, find
)


@click.group(help="""
                            ChRIS-File-System -- cfs

A workable demonstration/proof-of-concept of a File-System
"implementation" on the ChRIS backend. In this experiment, CUBE
is imagined to organize its internal data-verse pervasively using
conventional file system concepts, i.e. files organized in nested
directories.
""")
@click.pass_context
def cfs(ctx) -> None:
    pass

cfs.add_command(cp.cp)
cfs.add_command(cd.cd)
cfs.add_command(pwd.pwd)
cfs.add_command(ls.ls)
cfs.add_command(mkdir.mkdir)
cfs.add_command(imp.imp)
cfs.add_command(find.find)
cfs.add_command(rm.rm)
cfs.add_command(shell.shell)
cfs.add_command(tree.tree)


if __name__ == '__main__':
    cfs()
