#! /bin/bash
#usage ./crash "Your app name"

appName=$1

if [ ! -f "symbolicatecrash" ] ;then
    complierpath="/Applications/Xcode.app"
    find $complierpath -name "symbolicatecrash" -exec cp {} `pwd` \;
fi

if [ ! -d "src" ] ;then
    mkdir src
fi

if [ ! -d "des" ] ;then
    mkdir src
fi

if [ ! -f "$appName.ipa" ] ;then
    echo "this is no $appName.ipa in `pwd`"
    exit
fi

if [ ! -d "$appName.dSYM" ] ;then
    echo "this is no $appName.dSYM in `pwd`"
    exit
fi

export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
rm des/*
for crash in `ls src`
do

    path=src/$crash
    ./symbolicatecrash $path $appName.app > des/$crash.log
done
echo "done"
