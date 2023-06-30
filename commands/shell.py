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

_shell:type          = core.Core

@click.command(help="""
                                CFS shell

An extremely "simple" CFS "shell". Run CFS commands from a shell-esque interface
that harkens back to the days of /bin/ash!

""")
@click.argument('directory', required = False)
@click.option('--prompt',
              is_flag=True,
              help='If set, print the CFS cwd as prompt')
@click.option('--promptReal',
              is_flag=True,
              help='If set, also print the "real" directory in the prompt')
def shell(directory:str, prompt, promptreal) -> None:
    # pudb.set_trace()
    SHELL:_shell  = _shell()
    SHELL.init()
    system  = jobber.Jobber({'verbosity': 1, 'noJobLogging': True})
    print(tabulate([["Welcome to the ChRIS File System Shell"]], tablefmt = 'simple_grid'))
    print("\ta thought experiment in code...\n")
    print("Enjoy your stay and please remain on the trails!")
    print("Oh, and don't feed the wildlife. It's not good for them.")
    print("\n\nType '--help' for a list of commands.")
    print("Type '<command> --help' for command specific help.")
    print("Type 'quit' to exit.")
    print("")

    while True:
        command:str             = input(f'{SHELL.pwd_prompt()}>$ ')
        if 'quit' in command.lower() or 'exit' in command.lower():
            sys.exit(0)
        else:
            d_run:dict[Any, Any]    = system.job_run(f"cfs {command}")

