import  os
from    typing      import Any
from    pydantic    import AnyHttpUrl, BaseSettings, AnyUrl
from    pathlib     import Path

class CoreIO(BaseSettings):
    metaDir:str             = '__CHRISOS'
    realRoot:str            = '/'
    homeDir:str             = '/home/rudolph'

class Meta(BaseSettings):
    cwd:str                 = 'cwd'
    fileStatTable:str       = '_fstat'
    fileMetaTable:str       = '_meta'

coreio:CoreIO   = CoreIO()
meta:Meta       = Meta()