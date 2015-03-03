#!/bin/bash
set -e
set -o pipefail

pushd `dirname $0` > /dev/null
. env/bin/activate

DJANGO_SETTINGS_MODULE=finance.settings python manage.py "$@"

popd > /dev/null
