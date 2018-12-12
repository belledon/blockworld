bootstrap: docker
from: continuumio/miniconda:latest


%runscript
  exec bash "$@"

%environment
 export PATH=$PATH:/sbin/
 export LC_ALL=en_US.UTF-8

%post
 
 apt-get update
 apt-get install -y build-essential
 apt-get clean