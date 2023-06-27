from    prototype   import *
from    config      import settings
from    pathlib     import Path
import  pudb

from    pfmisc      import Colors
import  sys

@constructor
def Core(this) -> None:
    # Type annotations are not supported on "this"
    this.core      = settings.coreio
    this.meta      = settings.meta
    this.realRoot  = Path(this.core.realRoot)
    this.metaRoot  = Path(this.core.realRoot) / Path(this.core.metaDir)
    this.cwdRec    = this.metaRoot / this.meta.cwd

def croot_check(this) -> bool:
    # pudb.set_trace()
    crootDir:Path   = Path(this.core.realRoot)
    exists:bool     = False
    exists          = crootDir.is_dir()
    return exists

def metaDirRoot_checkAndCreate(this) -> bool:
    # pudb.set_trace()
    if not this.croot_check():
        return False
    this.metaRoot.mkdir(parents = True, exist_ok = True)
    return True

def cwdRead(this) -> Path:
    # pudb.set_trace()
    if not this.cwdRec.is_file():
        this.cwdRec.touch(exist_ok = True)
        this.cwdRec.write_text('/')
    return Path(this.cwdRec.read_text())

def cwdWrite(this, path:Path) -> str:
    this.cwdRec.write_text(str(path))
    return str(path)

def init(this) -> bool:
    # pudb.set_trace()
    return this.metaDirRoot_checkAndCreate()

def cfs2fs(this, cfs:Path) -> Path:
    """
    Map a ChRIS cfs location to a real FS localtion

    Args:
        this (_type_): prototype self
        cfs (Path): cfs path

    Returns:
        Path: real FS path
    """
    # pudb.set_trace()
    FS:Path     = Path(f"{this.core.realRoot}{cfs}")
    return FS

def fs2cfs(this, fs:Path) -> Path:
    """
    Map a real FS location to a ChRIS cfs location

    Args:
        this (_type_): prototype self
        fs (Path): real file system path

    Returns:
        Path: cfs path
    """
    CFS:Path    = Path(str(fs).replace(this.core.realRoot, '', 1))
    return CFS

def path_expand(this, path:Path) -> Path:
    if "~" in str(path):
        path = Path(str(path).replace("~", this.core.homeDir))
    if not str(path).startswith('/'):
        path = this.cwdRead() / path
    path = path.resolve()
    return path

def pwd_prompt(this, **kwargs) -> str:
    b_realDir:bool  = False
    for k,v in kwargs.items():
        if k == 'realDir':  b_realDir = bool(v)
    path:Path   = Path('')
    if b_realDir:
        path    = this.cfs2fs(this.cwd())
    else:
        path    = this.cwd()
    if path == Path(this.core.homeDir): path = Path('~')
    return Colors.WHITE + Colors.BLUE_BCKGRND + str(path) + Colors.NO_COLOUR

def dir_checkExists(this, path:Path) -> bool:
    realFS:Path = this.cfs2fs(path)
    return realFS.is_dir()

def stderr(this, message:str, code:int=1) -> None:
    print(message)
    sys.exit(code)

Core.croot_check                    = croot_check
Core.metaDirRoot_checkAndCreate     = metaDirRoot_checkAndCreate
Core.init                           = init
Core.cwdRead                        = cwdRead
Core.cwd                            = cwdRead
Core.cwdWrite                       = cwdWrite
Core.cfs2fs                         = cfs2fs
Core.fs2cfs                         = fs2cfs
Core.path_expand                    = path_expand
Core.dir_checkExists                = dir_checkExists
Core.pwd_prompt                     = pwd_prompt
Core.stderr                         = stderr
