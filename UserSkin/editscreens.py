# -*- coding: utf-8 -*-

from debug import printDEBUG
from inits import *

from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from enigma import ePicLoad
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import *
from Tools.HardwareInfo import HardwareInfo 
from Tools.LoadPixmap import LoadPixmap
from Tools import Notifications
#system imports
from os import listdir, remove, rename, system, path, symlink, chdir, rmdir, mkdir
import shutil
import re
import xml.etree.cElementTree as ET
#Translations part
from Components.Language import language
currLang = language.getLanguage()[:2] #used for descriptions keep GUI language in 'pl|en' format
print currLang
try:
    from Components.LanguageGOS import gosgettext as _
    printDEBUG('LanguageGOS detected')
except:
    printDEBUG('LanguageGOS not detected, using local _')
    import gettext
    from translate import _

class UserSkinEditScreens(Screen):
    skin = """
  <screen name="UserSkinEditScreens" position="0,0" size="1280,720" title="UserSkin EditScreens" backgroundColor="transparent" flags="wfNoBorder">
    <eLabel position="0,0" size="1280,720" zPosition="-15" backgroundColor="#20000000" />
    <eLabel position=" 55,100" size="725,515" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="785,295" size="445,320" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="785,100" size="135,190" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="925,100" size="305,190" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position=" 55,620" size="290,55" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="350,620" size="290,55" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="645,620" size="290,55" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="940,620" size="290,55" zPosition="-10" backgroundColor="#202673ec" />
    <eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="645,675" size="290, 5" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="940,675" size="290, 5" zPosition="-10" backgroundColor="#202673ec" />
    <widget name="SkinPicture" position="935,115" size="284,160" backgroundColor="#004e4e4e" />
    <widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#004e4e4e" transparent="1" />
    <widget source="menu" render="Listbox" position="70,115" size="700,480" scrollbarMode="showOnDemand" transparent="1">
      <convert type="TemplatedMultiContent">
                                {"template":
                                        [
                                                MultiContentEntryPixmapAlphaTest(pos = (2, 2), size = (54, 54), png = 3),
                                                MultiContentEntryText(pos = (60, 2), size = (650, 24), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1), # name
                                                MultiContentEntryText(pos = (55, 26),size = (650, 30), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 2), # info
                                        ],
                                        "fonts": [gFont("Regular", 22),gFont("Regular", 14)],
                                        "itemHeight": 60
                                }
                        </convert>
    </widget>
    <widget name="Picture" position="808,342" size="400,225" alphatest="on" />
    <widget source="key_red" render="Label" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20b81c46" transparent="1" />
    <widget source="key_green" render="Label" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget source="key_yellow" render="Label" position="655,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget source="key_blue" render="Label" position="950,635" zPosition="1" size="260,25" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="#00ffffff" />
  </screen>
"""

    #init some variables
    EditedScreen = False
    myScreenName = None
    
    blockActions = False
    
    doNothing = 0
    doDelete = 1
    doExport = 2
    
    currAction = doNothing
    
    def __init__(self, session, ScreenFile = ''):
        Screen.__init__(self, session)
        self.session = session
        #valid ScreenFile is mandatory
        if ScreenFile == '':
            self.close()
            return
        elif not path.exists(ScreenFile):
            self.close()
            return

        self.ScreenFile = ScreenFile
        try:
            self.root = ET.parse(self.ScreenFile).getroot()
            self.myScreenName = self.root.find('screen').attrib['name']
        except:
            printDEBUG("%s -Is NOT proper xml file - END!!!" % self.ScreenFile)
            self.close()
            return
        printDEBUG("%s has been loaded successfully. :)" % self.ScreenFile)
        
        if self.myScreenName == None:
            myTitle=_("UserSkin %s - EditScreens") %  UserSkinInfo
        else:
            myTitle=_("UserSkin %s - Edit %s screen") %  (UserSkinInfo,self.myScreenName)
            
        self.setTitle(myTitle)
        try:
            self["title"]=StaticText(myTitle)
        except:
            pass
        
        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText("")
        self["key_yellow"] = StaticText("")
        self['key_blue'] = StaticText(_('Actions'))
        
        self["Picture"] = Pixmap()
        self["SkinPicture"] = Pixmap()
        
        menu_list = []
        self["menu"] = List(menu_list)
        
        self["shortcuts"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
        {
            "ok": self.keyOK,
            "cancel": self.keyExit,
            "red": self.keyExit,
            "green": self.keyGreen,
            "blue": self.keyBlue,
        }, -2)
        
        self.skin_base_dir = SkinPath
        #self.screen_dir = "allScreens"
        self.allScreens_dir = "allScreens"
        #check if we have preview files
        isPreview=0
        for xpreview in listdir(SkinPath + "allPreviews/"):
            if len(xpreview) > 4 and  xpreview[-4:] == ".png":
                isPreview += 1
            if isPreview >= 2:
                break
        if path.exists("%sUserSkinpics/install.png" % SkinPath):
            printDEBUG("SkinConfig is loading %sUserSkinpics/remove.png" % SkinPath)
            self.disabled_pic = LoadPixmap(cached=True, path="%sUserSkinpics/remove.png" % SkinPath)
        else:
            self.disabled_pic = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/UserSkin/pic/remove.png"))
        
        if not self.selectionChanged in self["menu"].onSelectionChanged:
            self["menu"].onSelectionChanged.append(self.selectionChanged)
        
        self.onLayoutFinish.append(self.LayoutFinished)

    def LayoutFinished(self):
        fileName = self.ScreenFile.replace('allScreens/','allPreviews/preview_').replace('.xml','.png')
        #print self.ScreenFile
        #print fileName
        if path.exists(fileName):
            self["SkinPicture"].instance.setScale(1)
            self["SkinPicture"].instance.setPixmapFromFile(fileName)
            self["SkinPicture"].show()
        
        self.createWidgetsList()
      
    def endrun(self):
        return
     
    def selectionChanged(self):
        print "> self.selectionChanged"
        sel = self["menu"].getCurrent()
        self.setPicture(sel[0])
        print sel

    def createWidgetsList(self):
        menu_list = []
        f_list = []
        NumberOfScreens = len(self.root.findall('screen'))
        if NumberOfScreens == 1:
            for child in self.root.findall('screen/*'):
                childTYPE = child.tag
                childTitle = ''
                childDescr = ''
                childAttributes = ''
                for key, value in child.items():
                    childAttributes += key + '=' + value + ' '
                if 'render' in child.attrib:
                    childTitle = child.attrib['render']
                if 'name' in child.attrib:
                    childDescr += _(' Name: ') + child.attrib['name']
                elif 'text' in child.attrib:
                    childDescr += _(' Text: ') + child.attrib['text']
                if 'source' in child.attrib:
                    childDescr += _(' Source: ') + child.attrib['source']
                if childDescr == '':
                    for key, value in child.items():
                        if childDescr == '':
                            childDescr += key + '=' + value
                        else:
                            childDescr += ' ' + key + '=' + value
                f_list.append((child, "%s %s" % (childTYPE, childTitle), childDescr, self.disabled_pic))
                printDEBUG('found <' + childTYPE + ' ' + childAttributes + '>')
        elif NumberOfScreens >= 1:
            f_list.append(('dummy', _("No support for multiple screen definitions in one file :("), '', self.disabled_pic))
            self.blockActions=True
        if len(f_list) == 0:
            f_list.append(("dummy", _("No widgets found"), '', self.disabled_pic))
            self.blockActions=True
        if self.blockActions == True:
            self['key_blue'].setText('')
        for entry in f_list:
            menu_list.append((entry[0], entry[1], entry[2], entry[3]))
        #print menu_list
        try:
          self["menu"].UpdateList(menu_list)
        except:
          print "Update asser error :(" #workarround to have it working on openpliPC
          myIndex=self["menu"].getIndex() #as an effect, index is cleared so we need to store it first
          self["menu"].setList(menu_list)
          self["menu"].setIndex(myIndex) #and restore
        self.selectionChanged()
      
    def setPicture(self, f):
        return
        pic = f.replace(".xml", ".png")
        #preview = self.skin_base_dir + "allPreviews/preview_" + pic
        if path.exists(self.skin_base_dir + "allPreviews/preview_" + pic):
            self["Picture"].instance.setScale(1)
            self["Picture"].instance.setPixmapFromFile(self.skin_base_dir + "allPreviews/preview_" + pic)
            self["Picture"].show()
        elif path.exists(self.skin_base_dir + "allPreviews/" + pic):
            self["Picture"].instance.setScale(1)
            self["Picture"].instance.setPixmapFromFile(self.skin_base_dir + "allPreviews/" + pic)
            self["Picture"].show()
        else:
            self["Picture"].hide()

#### KEYS ####
# RED, CANCEL
    def keyExit(self): 
        if self.EditedScreen == True:
            self.session.openWithCallback(self.keyExitRet, ChoiceBox, title = _("Exit options"), list = [(_("Exit without saving"),"exit"),(_("Save as & Exit"),"saveas"),(_("Save & Exit"),"save"),])
        else:
            self.close()

    def keyExitRet(self, ret):
        if ret:
            if ret[1] == 'exit':
                self.close()
            if ret[1] == 'save':
                self.keyExitRetSave()
            if ret[1] == 'saveas':
                self.keyExitRetSaveAs()
        else:
            self.close()
            
    def keyExitRetSaveAs(self):
        from Screens.VirtualKeyBoard import VirtualKeyBoard
        self.session.openWithCallback(self.keyExitRetSaveAsHasName, VirtualKeyBoard, title=(_("Enter filename")), text = path.basename(self.ScreenFile.replace('.xml','_new.xml')))
        pass
        
    def keyExitRetSaveAsHasName(self, callback = None):
        if callback is not None:
            self.ScreenFile = self.ScreenFile.replace(path.basename(self.ScreenFile), callback)
            if not self.ScreenFile.endswith('.xml'):
                self.ScreenFile += '.xml'
            self.keyExitRetSave()
        self.close()
        
    def keyExitRetSave(self):
        printDEBUG("Writing %s" % self.ScreenFile)
        with open(self.ScreenFile, "w") as f:
            f.write(ET.tostring(self.root, encoding='utf-8'))
        self.close()

# Blue
    def keyBlue(self):
        if self.blockActions == False:
            keyBlueActionsList=[
                (_("No action"), self.doNothing),
                (_("Delete"), self.doDelete),
                (_("Export"), self.doExport),
            ]
            self.session.openWithCallback(self.keyBlueEnd, ChoiceBox, title = _("Select Action:"), list = keyBlueActionsList)
        return

    def keyBlueEnd(self, ret):
        if ret:
            self.currAction = ret[1]
        else:
            self.currAction = self.doNothing
            
        if self.currAction == self.doNothing:
            self['key_green'].setText('')
        elif self.currAction == self.doDelete:
            self['key_green'].setText(_('Delete'))
        elif self.currAction == self.doExport:
            self['key_green'].setText(_('Export'))
        return

      
# OK
    def keyOK(self):
        pass

# Green
    def keyGreen(self):
        myIndex=self["menu"].getIndex()
        if self.currAction == self.doNothing:
            return
        elif self.currAction == self.doDelete:
            self.doDeleteAction(myIndex)
        elif self.currAction == self.doExport:
            self.doExportAction(myIndex)
            
    def doDeleteAction(self, what):
        childAttributes=''
        for key, value in self.root[0][what].items():
            childAttributes += key + '=' + value + ' '
        printDEBUG('doDeleteAction <%s %s>\n' % (self.root[0][what].tag,childAttributes))
            
        #self.createWidgetsList()
        
    def doExportAction(self, what):
        printDEBUG('doExportAction')
            
