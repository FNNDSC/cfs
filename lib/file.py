from sqlite3 import converters
from    prototype   import  *
from    config      import  settings
from    pathlib     import  Path
import  pudb
from    lib         import  core
from    pfmisc      import  Colors
import  os, sys
from    typing      import  Literal, LiteralString, Any, Union
import  csv
import  pandas      as      pd
import  datetime

@constructor # File ---------------------------------------
def File(this, cfsfile:Path, onObjStorage:bool = False) -> None:
    # Type annotations are not supported on "this"
    # add the core for some helper functions
    this.FS:type                = core.Core()

    if onObjStorage:
        cfsfile                 = cfsfile
    else:
        cfsfile                 = this.FS.path_expand(cfsfile)
    this.file:Path              = cfsfile
    this.link:Path              = Path('')

    this.realFSfunc             = None
    if onObjStorage:
        this.realFSfunc         = this.FS.cfs2ofs
    else:
        this.realFSfunc         = this.FS.cfs2fs

    try:
        this.stats              = this.realFSfunc(Path(this.file)).stat()
    except:
        this.stats              = None

    # and the object that will control the manifest
    if this.file.parent.name    == this.FS.core.metaDir:
        this.manifestFile:Path  =   Path(this.file)
    else:
        if this.realFSfunc(this.file).is_dir():
            this.manifestFile:Path  =   Path(this.file /
                                        Path(this.FS.core.metaDir) /
                                        Path(this.FS.meta.fileStatTable))
        else:
            this.manifestFile:Path  =   Path(this.file.parent /
                                        Path(this.FS.core.metaDir) /
                                        Path(this.FS.meta.fileStatTable))
    this.manifest                   = Manifest(this)

@property
def name(this) -> str:
    return this.file.name

@property
def owner(this) -> str:
    return "rudolph"

@property
def size(this) -> int:
    if this.stats:
        return this.stats.st_size
    else:
        return 0

@property
def refs(this) -> str:
    df_files:pd.DataFrame   = pd.read_csv(str(this.manifest.manifestRFS))
    df_refs:pd.DataFrame    = df_files[df_files['name'] == this.file.name]
    refs:str                = ''
    try:
        refs                = str(df_refs['refs'][df_refs.index.tolist()[0]])
    except:
        refs                = ''
    if refs == 'nan': refs  = ''
    return refs

@property
def ctime(this) -> str:
    return datetime.datetime.fromtimestamp(this.stats.st_mtime).strftime('%Y-%m-%d %H:%M')
    # return this.stats.st_mtime

def sourcePartition_resolve(source) -> tuple[Path, bool]:
    accessObjectStorage:bool    = False
    if 'obj:' in str(source):
        source                  = Path(str(source).replace('obj:', ''))
        accessObjectStorage     = True
    return source, accessObjectStorage

File.name                   = name
File.size                   = size
File.ctime                  = ctime
File.owner                  = owner
File.refs                   = refs

@constructor # Manifest ---------------------------------------
def Manifest(this, fileObj:type) -> None:
    # Define some data elements
    this.FS:type            = core.Core()
    this.fileObj:type       = fileObj
    this.manifest:Path      = fileObj.manifestFile
    this.manifestRFS:Path   = this.fileObj.realFSfunc(this.manifest)
    this.metaFields         = ['type', 'name', 'refs', 'owner', 'sharedWith', 'size', 'ctime', 'meta']

    # and initialize this manifest!
    manifest_init(this)

# @property
# def sharedWith(this, file:Path) -> list:
#     return []

def manifest_init(this) -> list:
    df:pd.DataFrame     = pd.DataFrame(columns = this.metaFields)
    l_ret:list          = []
    if not this.manifestRFS.is_file():
        this.manifestRFS.touch(exist_ok = True)
    if os.stat(str(this.manifestRFS)).st_size:
        return l_ret
    try:
        l_ret = this.metaFields
        df.loc[len(df)] = metaData_set( this.metaFields,
                                        manifest_create(this, 'dir'),
                                        name = '.')
        df.to_csv(str(this.manifestRFS), index = False, )
    except:
        pass
    return l_ret

def list_to_string(list_value) -> str:
  return '{}'.format(','.join(list_value))

def string_to_list(string) -> list:
    return string.split(',')

def metaData_set(l_keys:list, d_metaData:dict[str, Any], **kwargs) -> dict[str, Any]:
    """
    Any key in d_metaData (for key in l_keys) that is passed as in
    kwargs has its value changed to the kwargs value

    Args:
        l_keys (list): list of keys in dictionary to consider
        d_metaData (dict[str, Any]): the dictionary to update

    Returns:
        dict[str, Any]: updated dictionary
    """
    d_metaData  = {**d_metaData, **{key:kwargs[key] for key in l_keys if key in kwargs}}
    return d_metaData

def manifest_create(this, type:str = 'file') -> dict[str, Any]:
    d_metaData:dict[str, Any]   = {
        'name'      : this.fileObj.name,
        'type'      : type,
        'owner'     : this.fileObj.owner,
        'refs'      : '',
        'sharedWith': '',
        'size'      : this.fileObj.size,
        'ctime'     : this.fileObj.ctime,
        'meta'      : this.FS.meta.fileMetaTable
    }
    return d_metaData

def manifest_updateEntry(this,
                         d_fileInfo:dict[str, Any]  = dict(),
                         name:str                   = "",
                         l_skip:list                = []) -> dict[str, Any]:
    # pudb.set_trace()
    df:pd.DataFrame     = pd.read_csv(str(this.manifestRFS))
    search:str          = name
    if not name:
        search          = this.fileObj.name

    index:pd.Index      = df.index[df['name'] == search]

    if not d_fileInfo:
        d_fileInfo      = manifest_create(this)
    if len(index) > 0:
        for key in this.metaFields:
            if key not in l_skip:
                if key in d_fileInfo:
                    df.loc[index, key]  = d_fileInfo[key]
    else:
        df.loc[len(df)] = d_fileInfo
    df.sort_values(['type', 'name']).to_csv(str(this.manifestRFS), index = False)
    return d_fileInfo

def manifest_removeEntry(this, key:str, target:Any) -> pd.DataFrame:
    df:pd.DataFrame     = pd.read_csv(str(this.manifestRFS))
    df                  = df[df[key] != target]
    df.sort_values(['type', 'name']).to_csv(str(this.manifestRFS), index = False)
    return df

# Manifest.sharedWith     = sharedWith
Manifest.init           = manifest_init
Manifest.update_entry   = manifest_updateEntry
Manifest.create         = manifest_create
Manifest.remove_entry   = manifest_removeEntry