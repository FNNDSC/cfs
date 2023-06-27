import  click
from    prototype   import  *
from    lib         import  core
from    lib         import  file    as FILE
from    commands    import  imp, ls
from    pathlib     import  Path
import  pandas      as      pd
import  pudb

_cp:type        = imp._imp
_ls:type        = ls._ls
LS:_ls          = _ls()
LS.init()

def manifest_resolve(this, path:Path) -> tuple[Path, str]:
    manifestFile:Path       = Path('')
    file:str                = ""
    manifestFile, file      = this.manifest_get(path)
    return Path(manifestFile), file

def source_update(this, src:Path, srcfile:str, destLink:Path, destFile:str):
    srcFile:type                = FILE.File(src)
    manifestSrc:FILE.Manifest   = FILE.Manifest(srcFile)
    df_files:pd.DataFrame       = LS.files_get(src)

def file_vcopy(this, source:Path, target:Path):
    pudb.set_trace()

    source              = this.path_expand(source)
    target              = this.path_expand(target)
    sourcePath:Path     = Path('')
    sourceFile:str      = ""
    sourcePath, sourceFile  = this.manifest_resolve(Path(source))

    if this.cfs2fs(target.is_dir()):
        target          = target / Path(sourceFile)
    destPath:Path       = Path('')
    destFile:str        = ""
    destPath, destFile      = this.manifest_resolve(Path(target))

    sourceManifest:FILE.Manifest    = FILE.Manifest(FILE.File(source))
    df_source:pd.DataFrame  = LS.files_get(source)
    b_sourceUpdate:bool     = False
    if df_source['refs'].isnull().values.any():
        df_source['refs']   = f'->{target}'
        b_sourceUpdate      = True
    elif not str(target) in df_source['refs'][1]:
        df_source['refs']  += f';{target}'
        b_sourceUpdate      = True
    if b_sourceUpdate:
        sourceManifest.update_entry(df_source.to_dict(orient='records')[0])

    destManifest:FILE.Manifest      = FILE.Manifest(FILE.File(destPath))
    df_dest:pd.DataFrame    = LS.files_get(target)
    if df_dest.empty:
        df_dest             = df_source.copy()
        df_dest['refs']     = f'<-{source}'
    destManifest.update_entry(df_dest.to_dict(orient='records')[0])


_cp.manifest_resolve    = manifest_resolve
_cp.source_update       = source_update
_cp.file_vcopy          = file_vcopy

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
    CP:_cp          = _cp()
    CP.init()

    CP.file_vcopy(Path(source), Path(target))



    if recursive:
        print(f'Performing a recursive copy...')
    else:
        print(f'Performing a single copy...')
