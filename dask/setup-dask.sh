#!/bin/bash
set -e
VERSION=$1

virtualenv dask/py-dask$VERSION --python=python3
source dask/py-dask/bin/activate

# install binaries
python3 -m pip install "dask[complete]==$VERSION codecarbon"

# check
# python3
# import dask as dk
# dk.__version__
# dk.__git_revision__
# quit()

deactivate

./dask/ver-dask.sh
