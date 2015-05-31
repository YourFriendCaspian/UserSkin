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
#skrypt ma być w katalogu odpowiedniego Menu
if [ -z $1 ]; then
  myPath=`dirname $0`
else
  myPath=$1
fi

if [ -z $2 ]; then
  echo "MENU|Delete addons">$myPath/_Deleteaddons
  echo "ITEM|No addons path configured|DONOTHING|">>$myPath/_Deleteaddons
  echo "MENU|Download addons">$myPath/_Getaddons
  echo "ITEM|No addons path configured|DONOTHING|">>$myPath/_Getaddons
  exit 0
else
  skinPath=$2
fi

cd $skinPath

skinParts=`find -path "*/all*/*.xml"|sort`
skinPartsNo=`find -path "*/all*/*.xml"|grep -c ".xml"`
cd $skinPath/allBars/
skinBars=`find -type d 2>/dev/null|sort`
skinBarsNo=`find -type d -name 'bar_*' |grep -c ".xml"`

echo "MENU|Delete addons">$myPath/_Deleteaddons
if [ $skinBarsNo -lt 1 ] && [ $skinPartsNo -lt 1 ];then
  echo "ITEM|No addons installed|DONOTHING|">>$myPath/_Deleteaddons
fi

echo "MENU|Download addons">$myPath/_Getaddons
if [ ! -f $skinPath/skin.config ];then
  echo "ITEM|Skin does not have downloadable addons|DONOTHING|">>$myPath/_Getaddons
fi
. $skinPath/skin.config
if [ -z $addons ];then
  echo "ITEM|Skin does not have downloadable addons|DONOTHING|">>$myPath/_Getaddons
fi
#do tad sa tlumaczone
