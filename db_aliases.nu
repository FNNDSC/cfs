let-env REALROOT = "/home/rudolph/data/nCUBE"
let REALROOT = ([$env.REALROOT db] | str join '/')
alias c = cfs

def CUBE_show_keys [] {
    (cfs tree --filter __CHRISOS --mask $REALROOT /)
}

def CUBE_add_key [
    key:string
] {
    (cfs mkdir $key)
}

def CUBE_deref_key [
    key:string,
    attribs:string="name,refs"
] {
    (cfs ls $key --long --attribs $attribs)
}




