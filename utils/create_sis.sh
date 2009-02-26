#!/bin/bash

export LANG=en.UTF-8
export LC_ALL=en.UTF-8

SCRIPTDIR=$(dirname $0)
DIR=$1
DEV=$2

APP_FILENAME="gomarket"
APP_NAME="GoMarket"
APP_CAPTION="GoMarket"
APP_VENDOR="Triveos Tecnologia Ltda."

$SCRIPTDIR/ensymble.py py2sis --appname=$APP_NAME \
    --lang=EN --extrasdir=$APP_NAME --encoding=utf-8,utf-8 --icon=$DIR/icon.svg \
    --vendor="$APP_VENDOR" \
    $DIR $DIR/$APP_FILENAME.sis

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
