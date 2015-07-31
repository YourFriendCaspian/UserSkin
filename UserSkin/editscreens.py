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
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import *
from Tools.HardwareInfo import HardwareInfo 
from Tools.LoadPixmap import LoadPixmap
from Tools import Notifications
#system imports
from os import listdir, remove, rename, system, path, symlink, chdir, rmdir, mkdir
import shutil
import re
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

class EditScreens(Screen):
    skin = """
  <screen name="EditScreens" position="0,0" size="1280,720" title="UserSkin EditScreens" backgroundColor="transparent" flags="wfNoBorder">
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
    <!--widget source="session.VideoPicture" render="Pig" position="935,115" zPosition="3" size="284,160" backgroundColor="#ff000000">
    </widget-->
    <widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#004e4e4e" transparent="1" />
    <widget source="menu" render="Listbox" position="70,115" size="700,480" scrollbarMode="showOnDemand" transparent="1">
      <convert type="TemplatedMultiContent">
                                {"template":
                                        [
                                                MultiContentEntryPixmapAlphaTest(pos = (2, 2), size = (54, 54), png = 3),
                                                MultiContentEntryText(pos = (60, 2), size = (500, 22), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1), # name
                                                MultiContentEntryText(pos = (55, 24),size = (500, 32), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 2), # info
                                        ],
                                        "fonts": [gFont("Regular", 22),gFont("Regular", 16)],
                                        "itemHeight": 60
                                }
                        </convert>
    </widget>
    <widget name="Picture" position="808,342" size="400,225" alphatest="on" />
    <widget source="key_red" render="Label" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20b81c46" transparent="1" />
    <widget source="key_green" render="Label" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget source="key_yellow" render="Label" position="625,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget source="key_blue" render="Label" position="950,635" zPosition="1" size="260,25" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="#00ffffff" />
  </screen>
"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.EditScreen = False
        
        myTitle=_("UserSkin %s - EditScreens") %  UserSkinInfo
        self.setTitle(myTitle)
        try:
            self["title"]=StaticText(myTitle)
        except:
            pass
        
        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText("Save")
        self["key_yellow"] = StaticText("Enable/Disable")
        self['key_blue'] = StaticText('Add widget')
        
        self["Picture"] = Pixmap()
        
        menu_list = []
        self["menu"] = List(menu_list)
        
        self["shortcuts"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
        {
            "ok": self.runMenuEntry,
            "cancel": self.keyCancel,
            "red": self.keyCancel,
            "green": self.keyGreen,
            "blue": self.keyBlue,
        }, -2)
        
        self.currentSkin = config.skin.primary_skin.value.replace('skin.xml', '').replace('/', '')
        self.skin_base_dir = resolveFilename(SCOPE_SKIN, config.skin.primary_skin.value.replace('skin.xml', ''))
        if not self.skin_base_dir.endswith('/'):
            self.skin_base_dir = self.skin_base_dir + '/'
        #self.screen_dir = "allScreens"
        self.allScreens_dir = "allScreens"
        self.file_dir = "UserSkin_Selections"
        if path.exists("%sUserSkinpics/install.png" % SkinPath):
            printDEBUG("SkinConfig is loading %sUserSkinpics/install.png" % SkinPath)
            self.enabled_pic = LoadPixmap(cached=True, path="%sUserSkinpics/install.png" % SkinPath)
        else:
            self.enabled_pic = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/UserSkin/pic/install.png"))
        #check if we have preview files
        isPreview=0
        for xpreview in listdir(self.skin_base_dir + "allPreviews/"):
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
        
        self.onLayoutFinish.append(self.createWidgetsList)

    def keyBlue(self):
            #self.session.openWithCallback(self.endrun , MessageBox,_("To see previews install enigma2-skin-infinityhd-nbox-tux-full-preview package"), type = MessageBox.TYPE_INFO)
            self.session.open(MessageBox,_("To see previews install package:\nenigma2-skin-infinityhd-nbox-tux-full-preview"), type = MessageBox.TYPE_INFO)
            return

    def endrun(self):
        return
     
    def selectionChanged(self):
        print "> self.selectionChanged"
        sel = self["menu"].getCurrent()
        self.setPicture(sel[0])
        print sel
        if sel[3] == self.enabled_pic:
            self["key_green"].setText(_("Edit"))
            self.EditScreen = True
        elif sel[3] == self.disabled_pic:
            self["key_green"].setText("")
            self.EditScreen = False

    def createWidgetsList(self):
        menu_list = []
        f_list = []
        if len(f_list) == 0:
            f_list.append(("dummy", _("No widgets found"), '', self.disabled_pic))
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
      
    def createMenuList(self):
        chdir(self.skin_base_dir)
        f_list = []
        #printDEBUG('createMenuList> listing ' + self.skin_base_dir + self.allScreens_dir)
        if path.exists(self.skin_base_dir + self.allScreens_dir):
            list_dir = sorted(listdir(self.skin_base_dir + self.allScreens_dir), key=str.lower)
            for f in list_dir:
                if config.plugins.UserSkin.PIG_active.value == False:
                    if f.find('PIG') > 0 or f.find('PiG') > 0  or f.find('Pig') > 0 or f.lower().find('_pig') > 0:
                        continue
                if f.endswith('.xml') and f.startswith('skin_'):
                    friendly_name = f.replace("skin_", "")
                    friendly_name = friendly_name.replace(".xml", "")
                    friendly_name = friendly_name.replace("_", " ")
                    linked_file = self.skin_base_dir + self.file_dir + "/" + f
                    if path.exists(linked_file):
                        if path.islink(linked_file):
                            pic = self.enabled_pic
                        else:
                            remove(linked_file)
                            symlink(self.skin_base_dir + self.allScreens_dir + "/" + f, self.skin_base_dir + self.file_dir + "/" + f)
                            pic = self.enabled_pic
                    else:
                        pic = self.disabled_pic
                    f_list.append((f, friendly_name, self.getInfo(f) , pic))
        menu_list = []
        if len(f_list) == 0:
            f_list.append(("dummy", _("No User skins found"), '', self.disabled_pic))
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
        
    def getInfo(self, f):#currLang
        info = f.replace(".xml", ".txt")
        if path.exists(self.skin_base_dir + "allInfos/info_" + currLang + "_" + info):
            myInfoFile=self.skin_base_dir + "allInfos/info_" + currLang + "_" + info
        elif path.exists(self.skin_base_dir + "allInfos/info_en_" + info):
            myInfoFile=self.skin_base_dir + "allInfos/info_en_" + info
        else:
            return 'No Info'
        
        #with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        info = open(myInfoFile, 'r').read().strip()
        return info
            
    def setPicture(self, f):
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
    
    def keyCancel(self):
        self.close()

    def runMenuEntry(self):
        sel = self["menu"].getCurrent()
        if sel[3] == self.enabled_pic:
            remove(self.skin_base_dir + self.file_dir + "/" + sel[0])
        elif sel[3] == self.disabled_pic:
            symlink(self.skin_base_dir + self.allScreens_dir + "/" + sel[0], self.skin_base_dir + self.file_dir + "/" + sel[0])
        self.createWidgetsList()

    def keyGreen(self):
        if self.EditScreen == True:
            print "Init EditScreen :)"
        else:
            print "Nothing to Edit :("

