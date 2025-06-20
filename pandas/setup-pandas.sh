#!/bin/bash
set -e
VERSION=$1
PYTHON_VERSION=$2

# install all dependencies
# sudo apt-get update
# sudo apt-get install build-essential python3-dev python3-pip

rm -f -r pandas/py-pandas

virtualenv pandas/py-pandas --python=python3
source pandas/py-pandas/bin/activate

# install binaries
python3 -m pip install pandas==$VERSION pyarrow psutil codecarbon pyinstrument

deactivate

#./pandas/ver-pandas.sh

# # check
# source pandas/py-pandas/bin/activate
# python3
# import pandas as pd
# pd.__version__
# quit()
# deactivate
