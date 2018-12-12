#!/bin/bash

# This script will setup the project environment
# assuming you have singularity or conda installed

# Via singularity

# Via local conda

# # 1) Create the singularity container (requires sudo)
# # TODO make this not require sudo in publication by pulling.
# echo "Building container..."
# # chmod +x singularity/build_container.sh
# # CONT="env.simg"
# # cd singularity
# # if [ -f "$CONT" ]; then
# #     echo "Older container found...removing"
# #     rm -f "$CONT"
# # fi
# # sudo ./build_container.sh env.simg Singularity

# # 2) Use singularity container to create config
# # TODO Figure out logic
# echo "Setting up configs..."
# chmod +x run.sh
# ./run.sh "python3 config.py"
