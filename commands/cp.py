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

Cp:imp.Imp      = core.Core()

def manifest_resolve(this, path:Path) -> tuple[Path, str]:
    manifestFile:Path       = Path('')
    file:str                = ""
    manifestFile, file      = this.manifest_get(path)
    return Path(manifestFile), file

def source_update(this, src:Path, srcfile:str, destLink:Path, destFile:str):
    srcFile:type                = FILE.File(src)
    manifestSrc:FILE.Manifest   = FILE.Manifest(srcFile)
    df_files:pd.DataFrame       = LS.files_get(src)

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
    pudb.set_trace()

    source              = this.path_expand(source)
    target              = this.path_expand(target)
    # sourceManifest:Path = Path('')
    # sourceFile:str      = ""
    # sourceManifest, sourceFile  = this.manifest_resolve(Path(source))

    if this.cfs2fs(target).is_dir():
        target          = target / Path(source.name)
    # destManifest:Path   = Path('')
    # destFile:str        = ""
    # destManifest, destFile      = this.manifest_resolve(Path(target))

    return manifest_refsAdd(target,'<-', source,
                            manifest_refsAdd(source, '->', target)
                            )

    # sourceManifest:FILE.Manifest    = FILE.Manifest(FILE.File(source))
    # df_source:pd.DataFrame  = LS.files_get(source)
    # b_sourceUpdate:bool     = False
    # if df_source['refs'].isnull().values.any():
    #     df_source['refs']   = f'->{target}'
    #     b_sourceUpdate      = True
    # elif not str(target) in df_source['refs'][1]:
    #     df_source['refs']  += f';->{target}'
    #     b_sourceUpdate      = True
    # if b_sourceUpdate:
    #     sourceManifest.update_entry(df_source.to_dict(orient='records')[0])

    # destManifest:FILE.Manifest      = FILE.Manifest(FILE.File(destPath))
    # df_dest:pd.DataFrame    = LS.files_get(target)
    # if df_dest.empty:
    #     df_dest             = df_source.copy()
    #     df_dest['refs']     = f'<-{source}'
    # destManifest.update_entry(df_dest.to_dict(orient='records')[0])


Cp.manifest_resolve    = manifest_resolve
Cp.source_update       = source_update
Cp.file_copy           = file_copy

# Cp:_Cp                  = _Cp()
Cp.__proto__            = imp.Imp

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
    pudb.set_trace()
    # Here we define the prototypical inheritance:
    # CP inherits from an existing IMP object, with
    # CP specific overwrites of some methods.

    Cp.file_copy(Path(source), Path(target))



    if recursive:
        print(f'Performing a recursive copy...')
    else:
        print(f'Performing a single copy...')
