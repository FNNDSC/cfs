__version__ = '0.9.9'

import  pudb

import  click

from commands import (cp, cd, pwd, ls, mkdir, imp, shell)


@click.group(help="""
                            ChRIS-File-System -- cfs

A workable demonstration/proof-of-concept of a File-System
"implementation" on the ChRIS backend. The core idea is to
present the model of files / directories to clients, but to
implement meta-based operations on the actual physical
storage medium *within* ChRIS.
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
cfs.add_command(shell.shell)

if __name__ == '__main__':
    cfs()
