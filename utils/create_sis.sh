#!/bin/bash

export LANG=en.UTF-8
export LC_ALL=en.UTF-8

SCRIPTDIR=$(dirname $0)
DIR=$1
DEV=$2

APP_FILENAME="gomarket"
APP_NAME="GoMarket"
APP_VERSION="0.1.0"
APP_CAPTION="GoMarket"
APP_VENDOR="Triveos Tecnologia Ltda."
APP_UID="$($SCRIPTDIR/ensymble.py genuid $APP_NAME | cut -d\  -f2)"

$SCRIPTDIR/ensymble.py simplesis --uid=$APP_UID --appname=$APP_NAME --version=$APP_VERSION \
    --lang=EN --icon=$DIR/icon.svg \
    --vendor="$APP_VENDOR" \
    $DIR $DIR

    # --shortcaption
    # --caption
    # --textfile
    # --cert
    # --privkey
    # --passphrase
    # --caps

if [ "$DEV" ]; then
    $SCRIPTDIR/send_py_to_s60 -d $2 $DIR
fi
