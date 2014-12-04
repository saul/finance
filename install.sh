#!/bin/bash
set -e
set -o pipefail

pushd `dirname $0` > /dev/null

echo Creating virtualenv...
python -m venv env
. env/bin/activate

echo
echo Installing Python dependencies...
pip install -r requirements.txt

echo
echo Updating...
./manage.sh update

popd
