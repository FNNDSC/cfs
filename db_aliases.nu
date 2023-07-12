let-env REALROOT = "/home/rudolph/data/nCUBE"
let REALROOT = ([$env.REALROOT db] | str join '/')
alias c = cfs

def CUBE_keys_show [] {
    (cfs tree --filter __CHRISOS --mask $REALROOT /)
}

def CUBE_key_create [
    key:string
] {
    (cfs mkdir $key)
}

def CUBE_data_show_at_key [
    key:string,
    attribs:string="name,refs"
] {
    (cfs ls $key --long --attribs $attribs)
}

def CUBE_data_deepCopy [
    src:string,
    dest:string
] {
    (cfs cp --recursive $src $dest)
}

def CUBE_data_shallowCopy [
    src:string,
    dest:string
] {
    (cfs cp $src $dest)
}

def CUBE_key_importData [
    path:string,
    key:string
] {
    (cfs imp $path $key)
}

