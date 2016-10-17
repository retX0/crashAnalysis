#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import os
import commands
import time

transfilename = 'trans.txt'

baseLocalize = "Localizable.strings"

special_char_reg="\\.*?[]*()"

# 文件后缀名
fileSuffix = ".m"
# 对应.m的使用格式前缀
localizeStrPrefix = "CustomString(@"
# 提取key的正则
findReg = '.*?CustomString\(@(".*?")\).*?'

projectname = "./Demo"

localizeDic = dict( en=(2, "English", projectname + "/en.lproj/Localizable.strings"),
                    zh=(3, "Chinese", projectname + "/zh-Hans.lproj/Localizable.strings") )


def timestr():
    return time.strftime( '%Y:%m:%d %H:%M:%S', time.localtime( time.time( ) ) )


def str_tofile(str, filename, isAppend=1):
    operator = '>'
    if isAppend == 1:
        operator = '>>'
    tmp=str.replace('"','\\"')
    # print "transfer after " + tmp
    commandStr = "echo \"%s\" %s %s" % (str.replace('"','\\"'), operator, filename)
    os.popen( commandStr )


def trans_str(str, char):
    return str.replace(char, '\\'+char)


def regex_relugar_str(str):
    for char in list(special_char_reg):
        str=trans_str(str, char)
    return str

def log(str, needtime=1):
    logstr = " exec command %s " % (str)
    if needtime == 1:
        logstr = timestr( ) + logstr;

    str_tofile( logstr, "localize.log" )


def warning(str):
    str_tofile( str, "warning.txt" )


def file_exist(path):
    if os.path.exists( transfilename ) == False:
        print "transfile %s not existed" % (transfilename)
        exit( -1 )


def execshell(commandStr):
    (status, ouput) = commands.getstatusoutput( commandStr )
    log( "%s \n status:%d\t output:%s"% (commandStr, status, ouput))
    return (status, ouput)

def execeute_regex(str, reg, group_index):
    match = re.search(reg, str)

    if not match :
        return None

    try:
        match_string = match.group(group_index)
        if not match_string:
            return None
        return match_string
    except:
        return None

def generate_string():
    commandStr = "find `pwd` -iname '*%s' -exec grep -r -n '%s' '{}' \; > /tmp/input.txt" % (fileSuffix, localizeStrPrefix)
    execshell( commandStr )


def clear():
    execshell( 'rm -rf /tmp/input.txt' )


def generate_base_localize_string():
    generate_string( )

    out = open( baseLocalize, 'w+' )
    filename = ""
    allLocalizeKey = [];
    for line in open( "/tmp/input.txt" ):
        searchRegStr = '[\/]([A-z\s]+%s):(\d+).*' % (fileSuffix, findReg);
        m = re.search( searchRegStr, line )

        if not m:
            continue

        tmpfilename = m.group( 1 )
        linenumber = m.group( 2 )

        m = re.findall(findReg, line)

        if not m:
            continue

        if tmpfilename != filename:
            out.write( "\n\n" )
            filename = tmpfilename
            out.write( "/*****************************" + filename + "*********************************/\n" )

        reloca = m.group( 3 )


        for value in m:

            newline = "%s=%s; //line:%s\n" % (value, value,linenumber);

            if value in allLocalizeKey:
                newline = "//" + newline
            else:
                allLocalizeKey.append( value )

            out.write( newline )

    out.close( )


def generate_all_localize_string():
    generate_base_localize_string( )

    for value in localizeDic.values( ):
        path = value[2]
        commandStr = "cp -R -f %s %s" % (baseLocalize, path)
        execshell( commandStr )

# 从文件获取翻译 格式 k \t l \t l
def  value_for_key(str, key):

    reg_str = '%s' % (regex_relugar_str(key));

    for i  in range(len(localizeDic.keys())):
        reg_str +='\t(".*?")'

    return re.search(reg_str, str)



def translate():
    generate_all_localize_string()

    execshell( 'rm -rf warning.txt' )

    transfile_content=open(transfilename).read()

    for value in localizeDic.values( ):
        out = open(value[2],'w+');

        tmp_buffer=""
        for line in open(baseLocalize):

            key = line.split('=')[0]
            match = value_for_key(transfile_content, key)

            if match:
                tmp_buffer += line.replace('='+key,'='+match.group(value[0] - 1))
            else:
                tmp_buffer += line.replace('='+key,'=""')
                warning_str = "%s 未翻译成 %s" %(key, value[1]);
                warning(str);

        out.write(tmp_buffer)
        out.close()

    clear( )


def backup():
    generate_string()

    out = open( "/tmp/backup.txt", 'w+' )
    all_language = ""
    for value in localizeDic.values( ):
        language = value[1]
        all_language = '%s\t"%s"' % (all_language, language)

    for line in open( "/tmp/input.txt" ):
        searchRegStr = '[\/]([A-z\s]+%s):(\d+).*%s' % (fileSuffix, findReg);

        m = re.search( searchRegStr, line )

        if not m:
            continue

        filename = m.group( 1 )

        m = re.findall(findReg, line)
        
        if not m:
            continue

        for value in m:

            newline = "%s=%s; //line:%s\n" % (value, value,linenumber);

            if value in allLocalizeKey:
                newline = "//" + newline
            else:
                allLocalizeKey.append( value )

            out.write( newline )
    out.close( )


    lastfilename='backup'

    for value in localizeDic.values( ):
        out = open( "/tmp/%s.txt" %(value[1]), 'w')
        path = value[2]

        res = ""
        file_content = open(path).read()

        for line in open("/tmp/%s.txt" %(lastfilename)):
            key = line.split('\t')[1]

            localize_language = localize_language_value(file_content, key)

            if localize_language:

                res += line.replace(value[1],localize_language);
            else:

                warning_str = "%s 未翻译成 %s" %(key, value[1]);
                warning(str);
                res += line.replace(value[1],"未翻译");

        out.write(res)
        out.close()
        lastfilename=value[1]

    os.popen('mv %s backup.txt' % (out.name))
    print 'backup to backup.txt done'


def localize_language_value(str, key):

    reg='%s.*?=.*?"(.*?)"' % (regex_relugar_str(key))
    match=re.search(reg,str)

    # print str

    if not match:
        return ""
    return match.group(1)



translate( )
# print "compeleted"
# backup()
