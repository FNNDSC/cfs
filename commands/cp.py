import  click
from    prototype   import  *
from    lib         import  core
from    lib         import  file    as FILE
from    commands    import  imp, ls
from    pathlib     import  Path
from    typing      import  Generator, Any
import  pandas      as      pd
import  pudb

_ls:type        = ls._ls
LS:_ls          = _ls()

_Cp:imp._Imp    = imp._Imp

def manifest_refsAdd(
        path:Path,
        refmark:str,
        ref:Path,
        df_ref:pd.DataFrame     = pd.DataFrame(),
        onObjectStorage:bool    = False
) -> pd.DataFrame:
    # pudb.set_trace()
    pathManifest:FILE.Manifest  = FILE.Manifest(FILE.File(path, onObjectStorage))
    df_file:pd.DataFrame        = LS.files_get(path, onObjectStorage = onObjectStorage)
    b_manifestUpdate:bool       = False
    if df_file['refs'].isnull().values.any():
        df_file['refs']         = f'{refmark}{ref}'
        b_manifestUpdate        = True
    elif df_file.empty:
        df_file                 = df_ref.copy()
        df_file['name']         = path.name
        df_file['refs']         = f'{refmark}{ref}'
        b_manifestUpdate        = True
    elif not str(ref) in df_file['refs'][df_file.index.tolist()[0]]:
        df_file['refs']         += f';{refmark}{ref}'
        b_manifestUpdate        = True
    if b_manifestUpdate:
        pathManifest.update_entry(df_file.to_dict(orient='records')[0])
    return df_file

def file_copy(this, source:Path, target:Path, fromObjectStorage:bool = False) -> pd.DataFrame:
    # pudb.set_trace()
    source              = this.path_expand(source)
    target              = this.path_expand(target)
    sourceRefs:str      = FILE.File(source, fromObjectStorage).refs
    if this.cfs2fs(target).is_dir():
        target          = target / Path(source.name)
    if sourceRefs:
        try:
            source, fromObjectStorage   = FILE.sourcePartition_resolve(
                Path(str(sourceRefs).split('<-')[1])
            )
        except:
            pass
    return manifest_refsAdd(target,'<-obj:', source,
                            manifest_refsAdd(
                                source, '->', target,
                                pd.DataFrame(),
                                fromObjectStorage)
                            )
def df_generator(df:pd.DataFrame) -> Generator[pd.Series, Any, None]:
    for _, row in df.iterrows():
        yield row

def wildcards_check(path:Path) -> tuple[Path, str]:
    wildcard:str    = ''
    if '*' in path.name:
        wildcard    = path.name
        path        = path.parent
    return path, wildcard

def source_resolve(src:Path) -> Path:
    wildcard:str            = ""
    base:Path               = Path('')
    base, wildcard          = wildcards_check(src)
    if wildcard:
        src                 = base
    else:
        src                 = base.parent
    return src

def copy_do(this, src:Path, dest:Path, show:bool = False) -> int:
    # pudb.set_trace()
    count:int               = 0
    iterator:Generator[pd.Series, Any, None]   = df_generator(LS.files_get(src))
    src                     = source_resolve(src)
    for target in iterator:
        sourceFile:Path     = src / Path(target['name'])
        if show:
            print(f"{sourceFile:50} -> [CFS]{dest}")
        this.copy(src / Path(target['name']), dest)
        count += 1
    return count

_Cp.copy                = file_copy
_Cp.copy_do             = copy_do

@click.command(help="""
                                copy files

This command "copies" files from one part of ChRIS "storage" to another. In reality, only
single actual copy of the file exists in object storage, and the "copy" operation edits
the database document at the target directory key.

It is more akin to a "hard" link in standard UNIX file systems since data is not actually
duplicated.

""")
@click.argument('source', required = True)
@click.argument('target', required = True)
@click.option('--show',
              is_flag = True,
              help    = 'If set, print the files as they are imported')
@click.option('--recursive',
              is_flag=True,
              help='If set, do a recursive copy')
def cp(source, target, recursive, show) -> int:
    # Here we define the prototypical inheritance:
    # We create an instance of Cp that is essentially a
    # "clone" of the "imp"ort copy. Once instantiated,
    # we overwrite for this instance the file_copy method
    Cp:_Cp          = _Cp()
    filesCopied:int = Cp.copy_do(Path(source), Path(target), show)

    return filesCopied
