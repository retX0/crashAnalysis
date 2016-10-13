#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import os
import commands
import time

transfilename="trans.txt"

baseLocalize="Localizable.strings"

fileSuffix=".m";#文件后缀名
localizeStrPrefix="CustomString(@";#对应.m的使用格式前缀
findReg="CustomString\(@(\".*?\")\)";#提取key的正则

projectname="./12"

localizeDic={
    'en':(2,"English",projectname+"/en.lproj/Localizable.strings"),
    'zh':(3,"Chinese",projectname+"/zh-Hans.lproj/Localizable.strings")
}

def timestr():
    return time.strftime('%Y:%m:%d %H:%M:%S',time.localtime(time.time()))

def strTofile(str, filename, isAppend = 1):
    operator='>'
    if isAppend == 1:
        operator='>>'
    commandStr="echo \"%s\" %s %s" % (str, operator, filename)
    os.popen(commandStr)

def log(str, needtime=1):

    logstr=" exec command " + str +" "
    if needtime == 1:
        logstr = timestr() + logstr;

    strTofile(logstr, "localize.log")

def warning(str):
    strTofile(str, "warning.txt")

def fileExist(path):
    if os.path.exists(transfilename) == False:
        print "transfile %s not existed" %(transfilename)
        exit(-1)

def execshell(commandStr):
    (status,ouput)=commands.getstatusoutput(commandStr)
    if status != 0:
        log(commandStr + "failed")
    log(commandStr + " output " +ouput)
    return (status, ouput)

def generateString():
    commandStr = "find `pwd` -iname '*%s' -exec grep -r -n '%s' '{}' \; > /tmp/input.txt" % (fileSuffix, localizeStrPrefix)
    execshell(commandStr)

def clear():
    execshell('rm -rf /tmp/input.txt')

def generateBaseLocalizeString():

    generateString()

    out=open(baseLocalize,'w+')
    filename=""
    allLocalizeKey=[];
    for line in open("input.txt"):
        searchRegStr='[\/]([A-z\s]+%s):(\d+).*%s' % (fileSuffix, findReg);
        m=re.search(searchRegStr,line)

        if m == None:
            continue

        tmpfilename=m.group(1)
        linenumber=m.group(2)
        reloca=m.group(3)
        if tmpfilename!=filename:
            out.write("\n\n")
            filename=tmpfilename
            out.write("/*****************************"+filename+"*********************************/\n")

        newline= "%s=%s; //line:%s\n" % (reloca, reloca, linenumber);

        if reloca in allLocalizeKey:
            newline="//"+newline
        else:
            allLocalizeKey.append(reloca)
        out.write(newline)

    out.close()

def generateAllLocalizeString():
    generateBaseLocalizeString()

    for value in localizeDic.values():
        path=value[2]
        commandStr="cp -R -f %s %s" % (baseLocalize, path)
        execshell(commandStr)

def lanauageVale(key, index):

    fileExist(transfilename)

    commandStr="grep -w \"%s\" %s | awk -F'\t' '{ print $1,\",\",$%d } '" % (key, transfilename, index)
    (status, output) = execshell(commandStr)

    if not output:
        return ""
    if output.__len__() < 1:
        return ""
    if status != 0:
        return ""

    output=tuple(eval(output))

    # print "\"%s\" equal \"%s\" %d" %(key, output[0], key==output[0]);
    if key == output[0]:
        return output[1]
    return ""
    # print "originkey is "+output[0]
    # return output[1]

def replaceString(filename, keyIndex, language):

    fileExist(filename)

    for line in open(filename):
        key=re.search('"(.*?)"=("[0-z\s]+")', line)

        #FIXME: no key error
        if not key:
            continue;

        key = key.group(1)
        transLanguage=lanauageVale(key, keyIndex)

        if not transLanguage :
            warning("no key for line "+line)
            continue

        if transLanguage.__len__() != 0:
            print transLanguage

            commandStr="sed -i .backup 's/='%s';/='%s';/g' %s" % (key, transLanguage, filename)
            execshell(commandStr)
        else:
            warning("%s translate to %s is not compelete" % (key, language));
    else:
        warning("no key for line "+line)

def translate():

    generateAllLocalizeString()

    for value in localizeDic.values():
        replaceString(value[2],value[0], value[1])
    clear()
#
# generAllLocalizeString()
# replaceString(chnLocalize, 3)
# replaceString(enLocalize, 2)
# clear()

execshell('rm -rf warning.txt')
translate()

