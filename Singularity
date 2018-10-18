bootstrap: localimage
from: base.simg

%setup

 if [ -d ${SINGULARITY_ROOTFS}/src ];then
     rm -r ${SINGULARITY_ROOTFS}/src
 fi
 mkdir ${SINGULARITY_ROOTFS}/src

%files
 setup.py /src/
 README.md /src/
 LICENSE /src/
 blockworld /src/blockworld

%post
 python3 -m pip install -e /src
