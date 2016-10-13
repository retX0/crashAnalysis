#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import os
import commands

baseLocalize="base.strings"
enLocalize="en.strings"
chnLocalize="chn.strings"

def gengrateString():
    os.popen('find . -iname \'*.m\' -exec grep -r -n \'CustomString(@\' \'{}\' \; > input.txt')

def clear():
    os.popen('rm -rf input.txt')

def generateBaseLocalizeString():
    out=open(baseLocalize,'w')
    filename=""
    for line in open("input.txt"):
        m=re.search('[\/]([a-zA-Z\s]+.m):(\d+).*CustomString\(@(".*")\)',line)

        if m == None:
            continue

        tmpfilename=m.group(1)
        linenumber=m.group(2)
        reloca=m.group(3)
        if tmpfilename!=filename:
            out.write("\n\n")
            filename=tmpfilename
            out.write("/*****************************"+filename+"*********************************/\n")

        newline= "%s=%s //line:%s\n" % (reloca, reloca, linenumber);
        out.write(newline)

    out.close()

def generAllLocalizeString():
    generateBaseLocalizeString()
    os.popen('cp '+baseLocalize+' '+ enLocalize);
    os.popen('cp '+baseLocalize+' '+ chnLocalize);

def getLanauageKey(key, index):
    commandStr="grep -w %s %s | awk -F'\t' '{ print $%d } '" % (key, 'trans.txt', index)
    # print "exec command " + commandStr
    (status, languageKey) = commands.getstatusoutput(commandStr)
    #FIXME:error handle
    return languageKey

def replaceString(filename, keyIndex):
    for line in open(filename):
        key=re.search('".*?"=("[0-z\s]+")', line)
        #FIXME: no key error
        if key != None:
            key = key.group(1)
            commandStr="sed -i .backup 's/=%s/=\"%s\"/g' %s" % (key, getLanauageKey(key, keyIndex), filename)
            print "exec command "+commandStr
            commands.getstatusoutput(commandStr)
            # commands.getstatusoutput('sed  -i.backup \'s/='+key+'/="'+getLanauageKey(key, keyIndex)+'"/g \' chn.strings');

gengrateString()
generAllLocalizeString()
replaceString(chnLocalize, 3)
replaceString(enLocalize, 2)
clear()
