#!/bin/bash

transfilename=trans.txt

enlocalization=123.txt
zhlocalization=123.txt

english(){
    grep -w ${1} $transfilename | awk -F"\t" '{print $2}'
}

chinese(){
     grep -w ${1} $transfilename | awk -F"\t" '{print $3}'
}

takeTransStr(){
    find . -iname '*.m' -exec grep -r -n 'CustomString(@' '{}' \; > tmp.txt
}

replace(){
    sed -in-place -e "s/=\"${1}\";/=\"${2}\";/g" c.strings
}

filename() {
	name="`echo "${1}" | sed "s/\([0-z\s]\{0,\}\)\.m\d\{0,\}/ \1 /g" | awk '{print $2}'`"
	echo $name
}

linenumber() {
	line="`echo "${1}" | sed "s/.*[0-z\s]\{0,\}\.m:\(.*\):/ \1/g" `"
	echo $line
}

toStandandFrom() {

    `takeTransStr`

    echo "" > $enlocalization
    echo "" > $zhlocalization

    filename=""

    while read line
    do

    	tmpfilename=`filename ${line}`
    	linenumber=`linenumber ${line}`
    	echo "line is ${linenumber}"
    	echo "linenumber is " $linenumber
    	if [ "$filename" != "$tmpfilename" ];then
    		filename=$tmpfilename
    		echo "/******************"$filename"******************/" >> $enlocalization
    	fi

    	echo "//LINE:" $linenumber >> $enlocalization

        echo $line
    done < tmp.txt
    rm -rf tmp.txt
}



toStandandFrom
#takeTransStr

#cat $transfilename | awk -F'\t' '{ print $1 }' > key.txt

#while read key
#do
#	# grep $key trans.txt | awk -F"\t" -v chn="" '{chn=$2}'
#	chn=`grep -w "${key}" trans.txt | awk -F"\t" -v chn="" '{print $3}'`
#	en=`grep -w "${key}" trans.txt | awk -F"\t" -v chn="" '{print $2}'`
#	replace "${key}" "${chn}"
#
#done < key.txt
#
#rm -rf key.txt
