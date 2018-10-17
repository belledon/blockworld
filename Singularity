bootstrap: docker
from: ubuntu:16.04

%setup
 if [ -d ${SINGULARITY_ROOTFS}/deps ];then
    rm -r ${SINGULARITY_ROOTFS}/deps
 fi

 if [ -d ${SINGULARITY_ROOTFS}/src ];then
     rm -r ${SINGULARITY_ROOTFS}/src
 fi
 mkdir ${SINGULARITY_ROOTFS}/src

 if [ -d ${SINGULARITY_ROOTFS}/mybin ];then
    rm -r ${SINGULARITY_ROOTFS}/mybin
 fi
 mkdir ${SINGULARITY_ROOTFS}/mybin


%files
 deps /deps
 setup.py /src/
 README.md /src/
 LICENSE /src/
 experiment /src/experiment
 mybin/* /mybin/

%environment
 export PATH=$PATH:/mybin/
 export LANG=en_US.UTF-8
 export TMPDIR=$PWD/.tmp

 if [ -d ${PWD}/.tmp ];then
    rm -rf ${PWD}/.tmp
 fi
 mkdir ${PWD}/.tmp

%runscript
  exec bash "$@"

%post
 apt-get update
 apt-get install -y graphviz git wget python3-tk ffmpeg
 python3 -m pip install --upgrade pip
 python3 -m pip install numpy \
         scipy \
         pandas \
         joblib \
         h5py \
         pillow \
         matplotlib \
         SQLAlchemy \
         pydot pyyaml networkx \
         shapely \
         pyyaml \
         graphviz \
         "dask[complete]" \
         pybullet
         
 python3 -m pip install -e /deps/dask-jobqueue
 python3 -m pip install -e /src

 chmod +x /mybin/*
