#!/bin/sh 
# @j00zek 2015 dla Graterlia
#
#Plik do generowania menu
#musi znajdować się w katalogu menu i jest zawsze uruchamiany przy wyborzez ikonki
#jeśli chcemy, aby menu było statyczne, to na początku wpisujemy exit 0
#Jeśli menu ma byc dynamiczne to tutaj je sobie tworzymy przed każdym wejściem do niego
#
#struktura prosta jak budowa cepa,
#pierwsza linia zawiera nazwę menu
#MENU|<NAZWA Menu>
#
#kolejne linie zawierają poszczególne pozycje według schematu:
#ITEM|<Nazwa opcji>|Typ opcji [CONSOLE|MSG|RUN|SILENT|YESNO|APPLET]|<nazwa skryptu do uruchomienia>
#
#CONSOLE wyświetla okno konsoli i wszystko co się w nim dzieje
#MSG uruchamia w tle skrypt i wyświetla wiadomość zawierającą to co zwróci skrypt
#RUN uruchamia skrypt w tle i potwierdza jego wykonanie
#SILENT uruchamia skrypt w tle
#YESNO pyta sie czy uruchomic skrypt
#

if [ -z $2 ]; then
  echo "MENU|Delete addons">/tmp/_Deleteaddons
  echo "ITEM|No addons path configured|DONOTHING|">>/tmp/_Deleteaddons
  echo "MENU|Download addons">/tmp/_Getaddons
  echo "ITEM|No addons path configured|DONOTHING|">>/tmp/_Getaddons
  echo "MENU|Download additional Components/plugins">/tmp/_Getcomponents
  echo "ITEM|Components path not configured|DONOTHING|">>/tmp/_Getcomponents
  exit 0
else
  skinPath=$2
fi

cd $skinPath

skinParts=`find -path "*/all*/*.xml"|sort|sed 's;^./;;'`
skinPartsNo=`find -path "*/all*/*.xml"|grep -c ".xml"`
cd $skinPath/allBars/
skinBars=`find -name "*bar_*.menu" -type d 2>/dev/null|sort|sed 's;^./;;'`
skinBarsNo=`find -type d -name 'bar_*' |grep -c ".menu"`

echo "MENU|Delete addons">/tmp/_Deleteaddons
if [ $skinBarsNo -lt 1 ] && [ $skinPartsNo -lt 1 ];then
  echo "ITEM|No addons installed|DONOTHING|">>/tmp/_Deleteaddons
fi

for addon in $skinBars
do
  addonName=`echo $addon|sed 's/\..*$//'`
  echo $addonName
  echo "ITEM|$addonName|SILENT|/bin/rm -rf $skinPath/allBars/$addon">>/tmp/_Deleteaddons
done
for addon in $skinParts
do
  addonName=`echo $addon|sed 's/^.*\/\(.*\)\.xml/\1/'`
  echo $addonName
  echo "ITEM|$addonName|SILENT|/bin/rm -rf $skinPath/$addon">>/tmp/_Deleteaddons
done

##############################
echo "MENU|Download addons">/tmp/_Getaddons
if [ ! -f $skinPath/skin.config ];then
  echo "ITEM|Skin does not have downloadable addons|DONOTHING|">>/tmp/_Getaddons
fi
. $skinPath/skin.config
if [ -z $addons ];then
  echo "ITEM|Skin does not have downloadable addons|DONOTHING|">>/tmp/_Getaddons
fi

#curl -s --ftp-pasv $addons 1>/dev/null 2>%1
#[ $? -gt 0 ] && addons="$addons/"
addons="$addons/"
#echo $addons
DownloadableAddons=`curl -s --ftp-pasv $addons -o -|awk '{print $9}'|sort`

for addon in $DownloadableAddons
do
  addonName=`echo $addon|sed 's/\..*$//'`
  echo $addonName
  echo "ITEM|$addonName|CONSOLE|InstallAddon.sh $addon $skinPath">>/tmp/_Getaddons
done
##############################
echo "MENU|Download additional Components/plugins">/tmp/_Getcomponents
if [ ! -f $skinPath/skin.config ];then
  echo "ITEM|Skin does not have downloadable components|DONOTHING|">>/tmp/_Getcomponents
fi
. $skinPath/skin.config
if [ -z $components ];then
  echo "ITEM|Skin does not have downloadable components|DONOTHING|">>/tmp/_Getcomponents
fi

addons="$components/"
#echo $addons
DownloadableAddons=`curl -s --ftp-pasv $addons -o -|awk '{print $9}'|sort`

for addon in $DownloadableAddons
do
  addonName=`echo $addon|sed 's/\..*$//'`
  echo $addonName
  echo "ITEM|$addonName|CONSOLE|InstallAddon.sh $addon $skinPath">>/tmp/_Getcomponents
done

