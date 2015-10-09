#!/bin/sh 
# @j00zek 2015 dla Graterlia
#
#File generates a menu file
#have to be in menu folder and is always run when entering the menu
#jeśli chcemy, aby menu było statyczne, to na początku wpisujemy exit 0
#Jeśli menu ma byc dynamiczne to tutaj je sobie tworzymy przed każdym wejściem do niego
#
#struktura prosta jak budowa cepa,
#pierwsza linia zawiera nazwę menu
#MENU|<Name of Menu>
#
#kolejne linie zawierają poszczególne pozycje według schematu:
#ITEM|<Nazwa opcji>|Typ opcji [CONSOLE|MSG|RUN|SILENT|YESNO|APPLET]|<nazwa skryptu do uruchomienia>
#
#CONSOLE run script in console window
#MSG run script in background and displays message with returned value
#RUN run script in bacground and confires it has been run
#SILENT run script in background, no visible actions
#YESNO ask for confirmation to run the script or not
#

targetImage=""

if [ -e /usr/lib/enigma2/python/Plugins/SystemPlugins/VTIPanel ];then
  targetImage="VTI"
else
  targetImage="OpenPLI"
fi

myPath=`dirname $0`

cd $myPath

SkinImporters=`find  -type f -name *$targetImage.init -printf "%f\n"`

echo "MENU|Import foreign skin">/tmp/_Skins2Import
if [ -z "$SkinImporters" ];then
  echo "ITEM|No import scripts for current image available|DONOTHING|">>/tmp/_Skins2Import
  exit 0
fi

for SkinImporter in $SkinImporters
do
  SkinImporterName="`echo $SkinImporter|sed 's/\..*$//'|sed 's/_/ /g'`"
  echo "ITEM|$SkinImporterName|CONSOLE|$myPath/$SkinImporter">>/tmp/_Skins2Import
done
