import  click
from    prototype   import  *
from    lib         import  core
from    lib         import  file    as FILE
from    commands    import  imp, ls
from    pathlib     import  Path
import  pandas      as      pd
import  pudb

_ls:type        = ls._ls
LS:_ls          = _ls()

_Cp:imp._Imp    = imp._Imp

def manifest_refsAdd(path:Path, refmark:str, ref:Path, df_ref:pd.DataFrame=pd.DataFrame()) \
    -> pd.DataFrame:
    pathManifest:FILE.Manifest  = FILE.Manifest(FILE.File(path))
    df_file:pd.DataFrame        = LS.files_get(path)
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

def file_copy(this, source:Path, target:Path) -> pd.DataFrame:
    # pudb.set_trace()
    source              = this.path_expand(source)
    target              = this.path_expand(target)
    sourceRefs:str      = FILE.File(source).refs
    if sourceRefs:
        try:
            source      = Path(str(sourceRefs).split('<-')[1])
        except:
            pass
    if this.cfs2fs(target).is_dir():
        target          = target / Path(source.name)
    return manifest_refsAdd(target,'<-', source,
                            manifest_refsAdd(source, '->', target)
                            )

# _Cp.manifest_resolve    = manifest_resolve
# _Cp.source_update       = source_update

@click.command(help="""
                                copy files

This command "copies" files from one part of ChRIS storage to another. It is
more akin to a "symbolic" link in standard UNIX file systems since data is
not actually duplicated. Rather, meta-data is stored in the hidden _fstat
file of the __CHRISOS folder in a given directory.

""")
@click.argument('source', required = True)
@click.argument('target', required = True)
@click.option('--recursive',
              is_flag=True,
              help='If set, do a recursive copy')
def cp(source, target, recursive) -> None:
    # pudb.set_trace()
    # Here we define the prototypical inheritance:
    # We create an instance of Cp that is essentially a
    # "clone" of the "imp"ort copy. Once instantiated,
    # we overwrite for this instance the file_copy method
    Cp:_Cp          = _Cp()
    Cp.file_copy    = file_copy

    Cp.file_copy(Path(source), Path(target))

    if recursive:
        print(f'Performing a recursive copy...')
    else:
        print(f'Performing a single copy...')
