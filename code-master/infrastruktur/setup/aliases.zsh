# RoboCup
# A small collection of aliases and functions for our tools, enviroments and building our code
## Locations
export BITBOTS_CODE_DIR=~/git
export BITBOTS_CHROOT_DIR=~/darwin-chroot

# Add an alias for programs with defines additional options, so that the alias is defined, when the program is installed, but the alias won't be defined, if the program is not installed
function p_alias {
    al=${1/=*/}
    #echo "search $al"
    found=$(bash -c "for i in ${PATH//:/ } ; do find \$i -name $al;done")
    if ! [ -z "$found" ] ; then
        alias $@
        #echo alias $@
    fi
}

## ChRoot
#alias ChRoot="sudo mount --bind ~/Pictures/darwin-testimages ${BITBOTS_CHROOT_DIR}/home/darwin/Pictures && sudo ~/darwin-chroot/startup.sh ${BITBOTS_CODE_DIR} ; sudo umount ${BITBOTS_CHROOT_DIR}/home/darwin/Pictures"
alias ChRoot="sudo ${BITBOTS_CHROOT_DIR}/startup.sh ${BITBOTS_CODE_DIR}"

## Virtual env
alias activate='source ${BITBOTS_CODE_DIR}/.py-env/bin/activate'
alias reactivate='if [[ $VIRTUAL_ENV ]] ; then VENV="${VIRTUAL_ENV}" ; deactivate >/dev/null 2>&1 ; . ${VENV}/bin/activate; fi'
### Interactive Python interpreter in Virtual env
### The interactive python interpreter ipython and bpython didn't work fine inside an activated virtual-env, when not started directly inside, so here is a work around to start it inside if available
p_alias ipython='$(executable ipython)'
p_alias bpython='$(executable bpython)'

## Tools
alias GLRobot="activate ; simulation >/dev/null 2>&1 & glrobot >/dev/null 2>&1 &"
alias rstat='export CUR=`pwd -L` && cd ${BITBOTS_CODE_DIR} && git status && cd $CUR'
alias robocup_export="export DEBUG=1 && export VISION_DEBUG=1 && export VISION_DEBUG_FRAME_SKIP=0 && export DEBUG_HOST=127.0.0.1 && export DEBUG_LEVEL=5"
alias gitroot='cd $(git rev-parse --show-toplevel)'

## Build definements
## Note these building aliases require the "correct" virtual-env location in the code folder, or at least a valid symbolic link.
## Otherwise the virtual-env has to be activated.
alias build='${BITBOTS_CODE_DIR}/build'
alias Qbuild="QUIET=1 build"
alias Rbuild="build Release"
alias QRbuild="Qbuild Release"
alias RWDbuild="build ReleaseWithDebInf"
alias QRWDbuild="QUIET=1 RWDbuild"
alias Cbuild="build --clean -e"
alias CEbuild="build --clean-env -e"
alias CBbuild="build --clean-build-path -e"
alias CGBuild="build --clean -DDEBUG_LEVEL=0 "

## Debugger
alias pygdb="gdb -args python"
### consider the "bitbots_debug" function


# Some defined functions to provide more features that it's possible with aliases
## Start gdb for our python executables e.g. bitbots_debug simulation
function bitbots_debug {
    if ! [[ $VIRTUAL_ENV ]];then
        activate
    fi
    pygdb $VIRTUAL_ENV/bin/$@
}

## find executables of a given program line ipython that can be installed on the system and in the virtual-env
function executables {
    echo $(echo "-c \"find ${PATH//:/ } -name $@ -executable\"" | xargs bash)
}
function executable {
    echo "$(executables $@ | sed -r 's/ .*//')"
}
## Surpress a programs output
function quiet {
    $@ >/dev/null 2>&1
}
## additionally run it in background
function bquiet {
    $@ >/dev/null 2>&1 &
}
