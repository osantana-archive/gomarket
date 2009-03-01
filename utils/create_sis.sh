#!/bin/bash
# 
#  create_sis.sh
#  comprices
#  
#  Created by Osvaldo Santana on 2009-02-27.
#  Copyright 2009 Triveos Tecnologia Ltda. All rights reserved.
# 

export LANG=en.UTF-8
export LC_ALL=en.UTF-8

usage() {
    echo "$0 srcdir resource_dir [target_device]"
}

SCRIPTDIR=$(dirname $0)
SRCDIR=$1
if [ ! "$SRCDIR" ]; then
    usage
    exit 1
fi

RSCDIR=$2
if [ ! "$RSCDIR" ]; then
    usage
    exit 1
fi

DESTDEV=$3
BUILDDIR="$SCRIPTDIR/pkg"

APP_FILENAME="comprices"
APP_NAME="ComPrices"
APP_VERSION="0.1.0"
APP_CAPTION="ComPrices"
APP_SHORTCAPTION="ComPrices"
APP_VENDOR="Triveos Tecnologia Ltda."
APP_UID="$($SCRIPTDIR/ensymble.py genuid $APP_NAME | cut -d\  -f2)"
SIGN_CERT="$HOME/.ssh/s60_cert.cer"
SIGN_KEY="$HOME/.ssh/s60_key.key"
CAPS="NetworkServices+ReadUserData+WriteUserData+LocalServices+UserEnvironment"
rm -rf $BUILDDIR
mkdir -p $BUILDDIR/root/data/$APP_FILENAME/
cp $SRCDIR/*.py $BUILDDIR/
cp -r $SRCDIR/simplejson $BUILDDIR/
cp $RSCDIR/icon.png $BUILDDIR/root/data/$APP_FILENAME/

$SCRIPTDIR/ensymble.py py2sis \
    --verbose \
    --vendor="$APP_VENDOR" \
    --cert="$SIGN_CERT" \
    --privkey="$SIGN_KEY" \
    --caps="$CAPS" \
    --appname="$APP_NAME" \
    --version="$APP_VERSION" \
    --caption="$APP_CAPTION" \
    --shortcaption="$APP_SHORTCAPTION" \
    --lang=EN \
    --extrasdir=root \
    --uid=$APP_UID \
    --icon=$RSCDIR/tiny_icon_final.svg \
    $BUILDDIR $SCRIPTDIR/build/$APP_FILENAME.sis

$SCRIPTDIR/ensymble.py mergesis \
    --verbose \
    --cert="$SIGN_CERT" \
    --privkey="$SIGN_KEY" \
    $SCRIPTDIR/build/$APP_FILENAME.sis \
    $SCRIPTDIR/PythonForS60_1_4_5_3rdEd.sis \
    $SCRIPTDIR/build/${APP_FILENAME}_bundle.sis

if [ "$DESTDEV" ]; then
    $SCRIPTDIR/send_py_to_s60 -d $DESTDEV $SCRIPTDIR/build/
fi
