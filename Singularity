bootstrap: localimage
from: base.simg

%setup

 if [ -d ${SINGULARITY_ROOTFS}/src ];then
     rm -r ${SINGULARITY_ROOTFS}/src
 fi
 mkdir ${SINGULARITY_ROOTFS}/src

%environment
 export PATH=$PATH:/mybin/:/blender/blender
 export LANG=en_US.UTF-8
 export TMPDIR=$PWD/.tmp

 if [ -d ${PWD}/.tmp ];then
    rm -rf ${PWD}/.tmp
 fi
 mkdir ${PWD}/.tmp

%files
 setup.py /src/
 README.md /src/
 LICENSE /src/
 blockworld /src/blockworld

%post
 python3 -m pip install bokeh
 python3 -m pip install -e /src
