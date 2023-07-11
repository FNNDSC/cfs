from    prototype   import *
from    config      import settings
from    pathlib     import Path
import  pudb
from    typing      import Callable
from    pfmisc      import Colors
import  sys

@constructor
def Core(this) -> None:
    # Type annotations are fully not supported on "this"
    this.core           = settings.coreio
    this.meta           = settings.meta
    this.dbRoot:Path    = Path(this.core.realRoot) / Path(this.core.dbPrefix)
    this.objRoot:Path   = Path(this.core.realRoot) / Path(this.core.objPrefix)
    this.dbMeta:Path    = this.dbRoot / Path(this.core.metaDir)
    this.objMeta:Path   = this.objRoot / Path(this.core.metaDir)
    this.cwdRec:Path    = this.dbMeta / this.meta.cwd

def manifests_touch(this, dir:Path) -> None:
    fstat:Path  = (dir / Path(this.meta.fileStatTable))
    meta:Path   = (dir / Path(this.meta.fileMetaTable))
    if not fstat.is_file():
        fstat.touch()
    if not meta.is_file():
        meta.touch()

def croot_createIfNotExist(this, dir:Path) -> bool:
    # pudb.set_trace()
    if not dir.is_dir():
        dir.mkdir(parents = True, exist_ok = True)
        this.manifests_touch(dir)
        return True
    return False

def metaRootObjDirs_checkAndCreate(this) -> list[bool]:
    """
    Create the db and obj "meta" dirs. These are the "first" meta
    dirs and they contain the file system manifest tables.

    Args:
        this (_type_): the core object

    Returns:
        bool: If already exist
    """
    # pudb.set_trace()

    return [croot_createIfNotExist(this, dir) for dir in [this.dbMeta, this.objMeta]]

def cwdRead(this) -> Path:
    # pudb.set_trace()
    if not this.cwdRec.is_file():
        this.cwdRec.touch(exist_ok = True)
        this.cwdRec.write_text('/')
    return Path(this.cwdRec.read_text())

def cwdWrite(this, path:Path) -> str:
    this.cwdRec.write_text(str(path))
    return str(path)

def init(this) -> list[bool]:
    # pudb.set_trace()
    return this.metaRootObjDirs_checkAndCreate()

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
    FS:Path     = Path(f"{this.dbRoot}{cfs}")
    return FS

def cfs2ofs(this, cfs:Path) -> Path:
    """
    Map a ChRIS cfs location to an object FS localtion

    Args:
        this (_type_): prototype self
        cfs (Path): cfs path

    Returns:
        Path: real FS path
    """
    # pudb.set_trace()
    FS:Path     = Path(f"{this.objRoot}{cfs}")
    return FS


def fs2ofs(this, fs:Path) -> Path:
    """
    Map a real FS location to a ChRIS object storage location

    Args:
        this (_type_): prototype self
        fs (Path): real file system path

    Returns:
        Path: cfs path
    """
    CFS:Path    = Path(str(fs).replace(this.objRoot, '', 1))
    return CFS

def fs2cfs(this, fs:Path) -> Path:
    """
    Map a real FS location to a ChRIS cfs location

    Args:
        this (_type_): prototype self
        fs (Path): real file system path

    Returns:
        Path: cfs path
    """
    CFS:Path    = Path(str(fs).replace(this.dbRoot, '', 1))
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

def manifest_get(this, path:Path, onobjectStorage:bool) -> tuple[Path, str]:
    path                    = this.path_expand(path)
    cfs2rfs:Callable        = this.cfs2fs if not onobjectStorage else this.cfs2ofs
    manifestFile:Path       = path / this.core.metaDir / this.meta.fileStatTable
    atRootDir:int           = 0
    file:str                = ''
    # Try and find the manifest file, and don't get trapped!
    # If we are "getting" a file, the manifest is off the parent
    while not cfs2rfs(manifestFile).is_file():
        file                = path.name
        path                = path.parent
        manifestFile        = path / this.core.metaDir / this.meta.fileStatTable
        if path == Path('/'):
            atRootDir += 1
        if atRootDir >= 2:
            manifestFile    = Path('/')
            break
    return manifestFile, file


# Core.croot_check                    = croot_check
Core.manifests_touch                = manifests_touch
Core.metaRootObjDirs_checkAndCreate = metaRootObjDirs_checkAndCreate
Core.init                           = init
Core.cwdRead                        = cwdRead
Core.cwd                            = cwdRead
Core.cwdWrite                       = cwdWrite
Core.cfs2fs                         = cfs2fs
Core.cfs2ofs                        = cfs2ofs
Core.fs2cfs                         = fs2cfs
Core.fs2ofs                         = fs2ofs
Core.path_expand                    = path_expand
Core.dir_checkExists                = dir_checkExists
Core.pwd_prompt                     = pwd_prompt
Core.stderr                         = stderr
Core.manifest_get                   = manifest_get