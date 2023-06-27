from sqlite3 import converters
from    prototype   import  *
from    config      import  settings
from    pathlib     import  Path
import  pudb
from    lib         import  core
from    pfmisc      import  Colors
import  os, sys
from    typing      import  Literal, LiteralString, Any
import  csv
import  pandas      as      pd
import  datetime

@constructor # File ---------------------------------------
def File(this, cfsfile:Path) -> None:
    # Type annotations are not supported on "this"
    # add the core for some helper functions
    this.FS:type                = core.Core()


    cfsfile                     = this.FS.path_expand(cfsfile)
    this.file:Path              = cfsfile
    this.link:Path              = Path('')

    this.stats                  = this.FS.cfs2fs(Path(this.file)).stat()

    # and the object that will control the manifest
    if this.file.parent.name    == this.FS.core.metaDir:
        this.manifestFile:Path  =   Path(this.file)
    else:
        this.manifestFile:Path  =   Path(this.file.parent /
                                    Path(this.FS.core.metaDir) /
                                    Path(this.FS.meta.fileStatTable))

@property
def name(this) -> str:
    return this.file.name

@property
def owner(this) -> str:
    return "rudolph"

@property
def size(this) -> int:
    return this.stats.st_size

@property
def ctime(this) -> str:
    return datetime.datetime.fromtimestamp(this.stats.st_mtime).strftime('%Y-%m-%d %H:%M')
    # return this.stats.st_mtime

File.name                   = name
File.size                   = size
File.ctime                  = ctime
File.owner                  = owner

@constructor # Manifest ---------------------------------------
def Manifest(this, fileObj:type) -> None:
    # Define some data elements
    this.FS:type            = core.Core()
    this.fileObj:type       = fileObj
    this.manifest:Path      = fileObj.manifestFile
    this.manifestRFS:Path   = this.FS.cfs2fs(this.manifest)
    this.metaFields         = ['name', 'type', 'owner', 'refs', 'sharedWith', 'size', 'ctime', 'meta']

    # and initialize this manifest!
    manifest_init(this)

# @property
# def sharedWith(this, file:Path) -> list:
#     return []

def manifest_init(this) -> list:
    # pudb.set_trace()
    df:pd.DataFrame     = pd.DataFrame(columns = this.metaFields)
    l_ret:list          = []
    if not this.manifestRFS.is_file():
        this.manifestRFS.touch(exist_ok = True)
    if os.stat(str(this.manifestRFS)).st_size:
        return l_ret
    try:
        l_ret = this.metaFields
        df.loc[len(df)] = manifest_create(this, 'dir')
        df.to_csv(str(this.manifestRFS), index = False, )
    except:
        pass
    return l_ret

def list_to_string(list_value) -> str:
  return '{}'.format(','.join(list_value))

def string_to_list(string) -> list:
    return string.split(',')

def manifest_create(this, type:str = 'file') -> dict[str, Any]:
    if type == 'file':
        d_metaData:dict[str, Any]   = {
            'name'      : this.fileObj.name,
            'type'      : 'file',
            'owner'     : this.fileObj.owner,
            'refs'      : '',
            'sharedWith': '',
            'size'      : this.fileObj.size,
            'ctime'     : this.fileObj.ctime,
            'meta'      : this.FS.meta.fileMetaTable
        }
    else:
        fileStat:type   = File(this.manifest)
        d_metaData:dict[str, Any]   = {
            'name'      : '.',
            'type'      : 'dir',
            'owner'     : fileStat.owner,
            'refs'      : '',
            'sharedWith': '',
            'size'      : 0,
            'ctime'     : fileStat.ctime,
            'meta'      : this.FS.meta.fileMetaTable
        }
    return d_metaData

def manifest_updateEntry(this, d_fileInfo:dict[str, Any] = dict(), name:str="") -> dict[str, Any]:
    # pudb.set_trace()
    df:pd.DataFrame             = pd.read_csv(str(this.manifestRFS))
    search:str                  = name
    if not name:
        search                  = this.fileObj.name

    index:pd.Index              = df.index[df['name'] == search]

    if not d_fileInfo:
        d_fileInfo              = manifest_create(this)
    if len(index) > 0:
        for key in this.metaFields:
            df.loc[index, key]  = d_fileInfo[key]
    else:
        df.loc[len(df)]         = d_fileInfo
    df.to_csv(str(this.manifestRFS), index = False)
    return d_fileInfo

# Manifest.sharedWith     = sharedWith
Manifest.init           = manifest_init
Manifest.update_entry   = manifest_updateEntry
Manifest.create         = manifest_create