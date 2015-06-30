# -*- coding: utf-8 -*-
# @j00zek 2014/2015 dla Graterlia

from enigma import eConsoleAppContainer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel
from translate import _
from inits import *
#
from Components.Pixmap import Pixmap
from enigma import ePicLoad, ePoint, getDesktop, eTimer, ePixmap
from os import system as os_system, popen as os_popen, path
#from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox

def substring_2_translate(text):
    to_translate = text.split('_(', 2)
    text = to_translate[1]
    to_translate = text.split(')', 2)
    text = to_translate[0]
    return text
    
def __(txt):
    if txt.find('_(') == -1:
        txt = _(txt)
    else:
        index = 0
        while txt.find('_(') != -1:
            tmptxt = substring_2_translate(txt)
            translated_tmptxt = _(tmptxt)
            txt = txt.replace('_(' + tmptxt + ')', translated_tmptxt)
            index += 1
            if index == 10:
                break

    return txt

class UserSkinconsole(Screen):
    #TODO move this to skin.xml
    skin = """
        <screen position="center,center" size="550,400" title="Command execution..." >
            <widget name="text" position="0,0" size="550,400" font="Console;14" />
        </screen>"""
        
    def __init__(self, session, title = "UserSkinconsole", cmdlist = None, finishedCallback = None, closeOnSuccess = False):
        Screen.__init__(self, session)

        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self.errorOcurred = False

        self["text"] = ScrollLabel("")
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"], 
        {
            "ok": self.cancel,
            "back": self.cancel,
            "up": self["text"].pageUp,
            "down": self["text"].pageDown
        }, -1)
        
        self.cmdlist = cmdlist
        self.newtitle = title
        
        self.onShown.append(self.updateTitle)
        
        self.container = eConsoleAppContainer()
        self.run = 0
        self.container.appClosed.append(self.runFinished)
        self.container.dataAvail.append(self.dataAvail)
        self.onLayoutFinish.append(self.startRun) # dont start before gui is finished

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        self["text"].setText("" + "\n\n")
        print "TranslatedConsole: executing in run", self.run, " the command:", self.cmdlist[self.run]
        if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
            self.runFinished(-1) # so we must call runFinished manual

    def runFinished(self, retval):
        if retval:
            self.errorOcurred = True
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
                self.runFinished(-1) # so we must call runFinished manual
        else:
            #lastpage = self["text"].isAtLastPage()
            str = self["text"].getText()
            str += _("\nUse up/down arrows to scroll text. OK closes window");
            self["text"].setText(str)
            #if lastpage:
            self["text"].lastPage()
            if self.finishedCallback is not None:
                self.finishedCallback()
            if not self.errorOcurred and self.closeOnSuccess:
                self.cancel()

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)

    def dataAvail(self, str):
        #lastpage = self["text"].isAtLastPage()
        self["text"].setText(self["text"].getText() + __(str))
        #if lastpage:
        self["text"].lastPage()

############################################
class Cover2(Pixmap):
    def __init__(self):
        Pixmap.__init__(self)
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintIconPixmapCB)
        self.paramsSet = False

    def onShow(self):
        Pixmap.onShow(self)

    def paintIconPixmapCB(self, picInfo=None):
        #t = currentThread()
        ptr = self.picload.getData()
        if ptr != None:
            self.instance.setPixmap(ptr)
            self.show()

    def updateIcon(self, filename):
        #t = currentThread()
        if not self.paramsSet:
            self.picload.setPara((self.instance.size().width(), self.instance.size().height(), 1, 1, False, 1, "#00000000"))
            self.paramsSet = True
        self.picload.startDecode(filename)
############################################

class myMenu(Screen,):
    def __init__(self, session, MenuFolder = "" , MenuFile = '_MenuItems', MenuTitle = 'myMenu'):
        
        self.myList = []
        self.list = []
        self.myPath = MenuFolder
        self.MenuFile = "%s/%s" % (self.myPath,MenuFile)
        self.SkryptOpcji = ""
        self.PIC = ""
        picHeight = 0
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        if path.exists("%s/_MenuGenerator.sh" % self.myPath) is True:
            self.system( "%s/_MenuGenerator.sh %s %s" % (self.myPath, self.myPath, SkinPath) )
            if not path.exists(self.MenuFile) and path.exists('/tmp/%s' % MenuFile):
                self.MenuFile = '/tmp/%s' % MenuFile
        MyTitle = ""
        if path.exists(self.MenuFile) is True:
            with open (self.MenuFile, "r") as myMenufile:
                for MenuItem in myMenufile:
                    MenuItem = MenuItem.rstrip('\n') 
                    if not MenuItem or MenuItem[0] == '#': #omijamy komentarze
                        continue
                    if MenuItem[0:5] == "MENU|":
                        MyTitle = MenuItem.replace("MENU|","")
                    elif MenuItem[0:4] == "PIC|":
                        if path.exists( MenuItem.replace("PIC|","") ) is True:
                            self.PIC = MenuItem.replace("PIC|","")
                            picHeight = 236
                    elif MenuItem[0:5] == "ITEM|":
                        #teraz nierzemy pod uwage tylko te linie co mają odpowiednią ilość |
                        #print MenuItem
                        skladniki = MenuItem.replace("ITEM|","").split('|')
                        if len(skladniki) != 3:
                            continue
                        (NazwaOpcji, TypOpcji,  self.SkryptOpcji) = skladniki
                        if NazwaOpcji != "":
                            NazwaOpcji = _(NazwaOpcji)
                        self.myList.append( (NazwaOpcji, TypOpcji,  self.SkryptOpcjiWithFullPAth(self.SkryptOpcji)) )
                        self.list.append( NazwaOpcji )
                myMenufile.close()

        skin  = """<screen name="myMenu" position="center,center" size="300,450" title=" " >\n"""
        skin += """<widget name="list" position="0,0" size="300,400" scrollbarMode="showOnDemand" />\n"""
        skin += """<widget name="cover" zPosition="4" position="0,340" size="420,236" transparent="1" alphatest="blend" />"""
        skin += """</screen>"""

        self["cover"] = Cover2()

        self.skin = skin
        self.session = session
        Screen.__init__(self, session)

        self["list"] = MenuList(self.list)
        
        self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.run, "cancel": self.close}, -1)

        self.onLayoutFinish.append(self.onStart)
        self.visible = True
        self.setTitle(MenuTitle)

    def onStart(self):
        self["cover"].hide()
        if self.PIC != "" and path.exists( self.PIC ) is True:
            self["cover"].updateIcon( self.PIC )
            self["cover"].show()
    
    def YESNO(self, decyzja):
        if decyzja is False:
            return
        self.system("%s"  %  self.SkryptOpcji)

    def system(self,komenda):
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        os_system(komenda)
      
    def run(self):
        selecteditem = self["list"].getCurrent()
        if selecteditem is not None:
            for opcja in self.myList:
                if opcja[0] == selecteditem:
                    self.SkryptOpcji = opcja[2]
                    if opcja[1] == "CONSOLE":
                        self.session.openWithCallback(self.endrun ,UserSkinconsole, title = "%s" % selecteditem, cmdlist = [ ('%s' %  self.SkryptOpcji) ])
                    if opcja[1] == "YESNO":
                        self.session.openWithCallback(self.YESNO ,MessageBox,_("Execute %s?") % selecteditem, MessageBox.TYPE_YESNO)
                    if opcja[1] == "SILENT":
                        self.system("%s"  %  self.SkryptOpcji)
                        self.endrun()
                    elif opcja[1] == "RUN":
                        self.system("%s"  %  self.SkryptOpcji)
                        self.session.openWithCallback(self.endrun,MessageBox,_("%s executed!") %( selecteditem ), MessageBox.TYPE_INFO, timeout=5)
                    elif opcja[1] == "MSG":
                        msgline = ""
                        popenret = os_popen( self.SkryptOpcji)
                        for readline in popenret.readlines():
                            msgline += readline
                        self.session.openWithCallback(self.endrun,MessageBox, "%s" %( msgline ), MessageBox.TYPE_INFO, timeout=15)
                            

    def endrun(self, ret =0):
        #odświerzamy menu
        self.system( "%s/_MenuGenerator.sh %s %s" % (self.myPath, self.myPath, SkinPath) )
        self.reloadLIST()
        self.onStart()
        return
    
    def SkryptOpcjiWithFullPAth(self, txt):
        if not txt.startswith('/'):
            return ('%s/%s') %(self.myPath,txt)
        else:
            return txt
            
    def reloadLIST(self):
        #czyścimy listę w ten dziwny sposób, aby GUI działało, bo nie zmienimy objektów ;)
        while len(self.list) > 0:
            del self.myList[-1]
            del self.list[-1]
        if path.exists(self.MenuFile) is True:
            self["list"].hide()
            with open (self.MenuFile, "r") as myMenufile:
                for MenuItem in myMenufile:
                    MenuItem = MenuItem.rstrip('\n') 
                    if not MenuItem or MenuItem[0] == '#': #omijamy komentarze
                        continue
                    #interesują nas tylko pozycje menu
                    if MenuItem[0:5] == "ITEM|":
                        #teraz bierzemy pod uwage tylko te linie co mają odpowiednią ilość |
                        #print MenuItem
                        skladniki = MenuItem.replace("ITEM|","").split('|')
                        if len(skladniki) == 3:
                            (NazwaOpcji, TypOpcji, SkryptOpcji) = skladniki
                            if NazwaOpcji != "":
                                NazwaOpcji = _(NazwaOpcji)
                            self.myList.append( (NazwaOpcji, TypOpcji, self.SkryptOpcjiWithFullPAth(SkryptOpcji)) )
                            self.list.append( NazwaOpcji )
                myMenufile.close()
            myIdx = self["list"].getSelectionIndex()
            if myIdx > len(self.list) -1:
                self["list"].moveToIndex(len(self.list) -1)
            self["list"].show()
