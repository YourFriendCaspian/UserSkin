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
from enigma import ePicLoad,eLabel,gFont
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from skin import parseColor,parseFont
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
    <widget source="Title" render="Label" position="70,47" size="1100,43" font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#004e4e4e" transparent="1" />
    <!-- List -->
    <eLabel position=" 55,100" size="725,425" zPosition="-10" backgroundColor="#20606060" />
    <widget source="menu" render="Listbox" position="70,115" size="700,390" scrollbarMode="showOnDemand" transparent="1">
      <convert type="TemplatedMultiContent">
                                {"template":
                                        [
                                                MultiContentEntryPixmapAlphaTest(pos = (2, 2), size = (54, 54), png = 3),
                                                MultiContentEntryText(pos = (60, 2), size = (650, 24), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1), # name
                                                MultiContentEntryText(pos = (100, 26),size = (600, 30), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 2), # info
                                        ],
                                        "fonts": [gFont("Regular", 22),gFont("Regular", 14)],
                                        "itemHeight": 56
                                }
                        </convert>
    </widget>
    <!-- Preview -->
    <eLabel position="925,100" size="305,160" zPosition="-10" backgroundColor="#20606060" />
    <widget name="SkinPicture" position="930,105" size="295,150" backgroundColor="#004e4e4e" />
    
    <!-- Widget Details -->
    <eLabel position="55,530" size="725,90" zPosition="-10" backgroundColor="#20606060" />
    <widget name="widgetDetailsTXT" position="70,535" size="710,80" font="Regular;15" transparent="1"/>
    
    <!-- Preview text -->
    <eLabel position="785,530" size="445,90" zPosition="-10" backgroundColor="#20606060" />
    <widget name="PreviewFont" position="790,540" size="435,70" valign="center" font="Regular;20" transparent="1" foregroundColor="#00ffffff" />
    
    <!-- Preview pixmap -->
    <eLabel position="785,100" size="135,160" zPosition="-10" backgroundColor="#20606060" />
    <widget name="PixMapPreview" position="795,105" size="115,120" alphatest="on" />
    
    <!-- Preview on Screen -->
    <eLabel position="785,265" size="445,260" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="800,280" size="415,233" zPosition="-10" backgroundColor="#20909090" />
    <!--widget name="PixMapPictureInScale" position="808,284" size="400,225" alphatest="on" /-->
    <!-- BUTTONS -->
    <eLabel position=" 55,625" size="290,55" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="350,625" size="290,55" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="645,625" size="290,55" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="940,625" size="290,55" zPosition="-10" backgroundColor="#202673ec" />
    <widget source="key_red" render="Label" position="70,640" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20b81c46" transparent="1" />
    <widget source="key_green" render="Label" position="365,640" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget source="key_yellow" render="Label" position="655,640" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget source="key_blue" render="Label" position="950,640" zPosition="1" size="260,25" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="#00ffffff" />
  </screen>
"""

    #init some variables
    EditedScreen = False
    myScreenName = None
    currentScreenID = 0
    NumberOfScreens = 1
    
    blockActions = False
    
    doNothing = 0
    doDelete = 1
    doExport = 2
    doSave = 3
    doSaveAs = 4
    doImport = 5
    resizeFont = 6
    moveHorizontally = 7
    moveVertically = 8
    resizeHorizontally = 9
    resizeVertically = 10
    
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
            self.NumberOfScreens = len(self.root.findall('screen'))
        except:
            printDEBUG("%s -Is NOT proper xml file - END!!!" % self.ScreenFile)
            self.close()
            return
        printDEBUG("%s has been loaded successfully. :)" % self.ScreenFile)
        
        if self.myScreenName == None:
            myTitle=_("UserSkin %s - EditScreens") %  UserSkinInfo
        else:
            if self.NumberOfScreens == 1:
                myTitle=_("UserSkin %s - Edit %s screen") %  (UserSkinInfo,self.myScreenName)
            else:
                myTitle=_("UserSkin %s - Edit %s screen (1/%d)") %  (UserSkinInfo,self.myScreenName,self.NumberOfScreens)
            
        self.setTitle(myTitle)
        
        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText("")
        if self.NumberOfScreens == 1:
            self["key_yellow"] = StaticText("")
        else:
            self["key_yellow"] = StaticText(_("Switch screen"))
        self['key_blue'] = StaticText(_('Actions'))
        self["PreviewFont"] = Label()
        self["widgetDetailsTXT"] = Label()
        
        self["PixMapPreview"] = Pixmap()
        self["SkinPicture"] = Pixmap()
        
        menu_list = []
        self["menu"] = List(menu_list)
        
        self["shortcuts"] = ActionMap(["UserSkinActions"],
        {
            "ok": self.keyOK,
            "cancel": self.keyExit,
            "red": self.keyExit,
            "green": self.keyGreen,
            "yellow": self.keyYellow,
            "blue": self.keyBlue,
            "channelup": self.channelup,
            "channeldown": self.channeldown,
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
        #clear fields
        self["widgetDetailsTXT"].setText('')
        self["PreviewFont"].setText('')
        self["PixMapPreview"].hide()
        
        self.createWidgetsList()
      
    def createWidgetsList(self):
        menu_list = []
        f_list = []
        for child in self.root[self.currentScreenID].findall('*'):
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
            #printDEBUG('found <' + childTYPE + ' ' + childAttributes + '>')
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

#### Selection changed - display widgets

    def selectionChanged(self):
        #print "> self.selectionChanged"
        myIndex=self["menu"].getIndex()
        # widget details
        self["widgetDetailsTXT"].setText( ET.tostring(self.root[self.currentScreenID][myIndex]) )
        self.setPixMapPreview(myIndex)
        self.setPreviewFont(myIndex)

    def setPixMapPreview(self, myIndex):
        if not 'pixmap' in self.root[self.currentScreenID][myIndex].attrib:
            self["PixMapPreview"].hide()
            return
        pic = self.root[0][myIndex].attrib['pixmap']
        if path.exists(resolveFilename(SCOPE_SKIN, pic)):
            self["PixMapPreview"].instance.setScale(1)
            self["PixMapPreview"].instance.setPixmapFromFile(resolveFilename(SCOPE_SKIN, pic))
            self["PixMapPreview"].show()
        else:
            self["PixMapPreview"].hide()
            
    def setPreviewFont(self, myIndex):
        if not 'font' in self.root[self.currentScreenID][myIndex].attrib:
            self["PreviewFont"].setText('')
            return
        #### Now we know we have font, so we can preview it :)
        myfont = self.root[self.currentScreenID][myIndex].attrib['font']
        #print myfont
        self["PreviewFont"].instance.setFont(gFont(myfont.split(';')[0], int(myfont.split(';')[1])))
        if 'text' in self.root[self.currentScreenID][myIndex].attrib:
            self["PreviewFont"].setText('%s' % self.root[self.currentScreenID][myIndex].attrib['text'])
        else:
            self["PreviewFont"].setText(_('Sample Text'))
        if 'foregroundColor' in self.root[self.currentScreenID][myIndex].attrib:
            self["PreviewFont"].instance.setForegroundColor(parseColor(self.root[self.currentScreenID][myIndex].attrib['foregroundColor']))            
        else:
            self["PreviewFont"].instance.setForegroundColor(parseColor("#00ffffff"))            
        if 'backgroundColor' in self.root[self.currentScreenID][myIndex].attrib:
            self["PreviewFont"].instance.setBackgroundColor(parseColor(self.root[self.currentScreenID][myIndex].attrib['backgroundColor']))            

#### KEYS ####

#CHANNEL UP
    def channelup(self):
        self.EditedScreen = True
        myIndex=self["menu"].getIndex()
        if self.currAction == self.resizeFont and 'font' in self.root[self.currentScreenID][myIndex].attrib:
            myfont = self.root[self.currentScreenID][myIndex].attrib['font']
            mySize = int(myfont.split(';')[1]) + 1
            if mySize > 80:
                mySize = 80
            self.root[self.currentScreenID][myIndex].set('font',myfont.split(';')[0] + ';%d' % mySize)
        elif self.currAction == self.moveHorizontally and 'position' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['position']
            myX= int(myAttrib.split(',')[0]) + 1
            myY= int(myAttrib.split(',')[1])
            if myX > 1920:
                myX = 1920
            self.root[self.currentScreenID][myIndex].set('position','%d,%d' % (myX,myY))
        elif self.currAction == self.moveVertically and 'position' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['position']
            myX=int(myAttrib.split(',')[0])
            myY=int(myAttrib.split(',')[1]) + 1
            if myY > 720:
                myY = 720
            self.root[self.currentScreenID][myIndex].set('position','%d,%d' % (myX,myY))
        elif self.currAction == self.resizeVertically and 'size' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['size']
            myX=int(myAttrib.split(',')[0])
            myY=int(myAttrib.split(',')[1]) + 1
            if myY > 720:
                myY = 720
            self.root[self.currentScreenID][myIndex].set('size','%d,%d' % (myX,myY))
        elif self.currAction == self.resizeHorizontally and 'size' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['size']
            myX=int(myAttrib.split(',')[0]) + 1
            myY=int(myAttrib.split(',')[1])
            if myX > 1920:
                myX = 1920
            self.root[self.currentScreenID][myIndex].set('size','%d,%d' % (myX,myY))
          
        self.selectionChanged()
        
#CHANNEL DOWN
    def channeldown(self):
        myIndex=self["menu"].getIndex()
        self.EditedScreen = True
        if self.currAction == self.resizeFont and 'font' in self.root[self.currentScreenID][myIndex].attrib:
            myfont = self.root[self.currentScreenID][myIndex].attrib['font']
            mySize = int(myfont.split(';')[1]) - 1
            if mySize < 8:
                mySize = 8
            self.root[self.currentScreenID][myIndex].set('font',myfont.split(';')[0] + ';%d' % mySize)
        elif self.currAction == self.moveHorizontally and 'position' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['position']
            myX= int(myAttrib.split(',')[0]) - 1
            myY= int(myAttrib.split(',')[1])
            if myX < 0:
                myX = 0
            self.root[self.currentScreenID][myIndex].set('position','%d,%d' % (myX,myY))
        elif self.currAction == self.moveVertically and 'position' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['position']
            myX=int(myAttrib.split(',')[0])
            myY=int(myAttrib.split(',')[1]) - 1
            if myY < 0:
                myY = 0
            self.root[self.currentScreenID][myIndex].set('position','%d,%d' % (myX,myY))
        elif self.currAction == self.resizeVertically and 'size' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['size']
            myX=int(myAttrib.split(',')[0])
            myY=int(myAttrib.split(',')[1]) - 1
            if myY < 0:
                myY = 0
            self.root[self.currentScreenID][myIndex].set('size','%d,%d' % (myX,myY))
        elif self.currAction == self.resizeHorizontally and 'size' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['size']
            myX=int(myAttrib.split(',')[0]) - 1
            myY=int(myAttrib.split(',')[1])
            if myX < 0:
                myX = 0
            self.root[self.currentScreenID][myIndex].set('size','%d,%d' % (myX,myY))

        self.selectionChanged()
        
# Yellow
    def keyYellow(self):
        if self.NumberOfScreens >= 1:
            self.currentScreenID += 1
            if self.currentScreenID >= self.NumberOfScreens:
                self.currentScreenID = 0

            try:
                self.myScreenName = self.root[self.currentScreenID].attrib['name']
            except:
                self.myScreenName = _('UnknownName')
            myTitle=_("UserSkin %s - Edit %s screen (1/%d)") %  (UserSkinInfo,self.myScreenName,self.NumberOfScreens)
            print myTitle
            
            self.setTitle(myTitle)
            self["menu"].setIndex(0)
        #try:
            #self["Title"]=StaticText(myTitle)
        #except:
        #    pass
            self.createWidgetsList()

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
                (_("Move left/right"), self.moveHorizontally),
                (_("Move Up/Down"), self.moveVertically),
                (_("Resize left/right"), self.resizeHorizontally),
                (_("Resize Up/Down"), self.resizeVertically),
                (_("Change font size"), self.resizeFont),
                (_("Delete"), self.doDelete),
                (_("Export"), self.doExport),
                (_("Import"), self.doImport),
                (_("Save"), self.doSave),
                (_("Save as"), self.doSaveAs),
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
        #saving
        elif self.currAction == self.doSaveAs:
            self.keyExitRetSaveAs()
            return
        elif self.currAction == self.doSave:
            self.keyExitRetSave()
            return
        #manipulationf
        elif self.currAction == self.doDelete:
            self['key_green'].setText(_('Delete'))
        elif self.currAction == self.doExport:
            self['key_green'].setText(_('Export'))
        elif self.currAction == self.doImport:
            self['key_green'].setText(_('Import'))
        elif self.currAction == self.resizeFont:
            self['key_green'].setText(_('Change font size'))
        elif self.currAction == self.moveHorizontally:
            self['key_green'].setText(_('Move left/right'))
        elif self.currAction == self.moveVertically:
            self['key_green'].setText(_('Move Up/Down'))
        elif self.currAction == self.resizeHorizontally:
            self['key_green'].setText(_('Resize left/right'))
        elif self.currAction == self.resizeVertically:
            self['key_green'].setText(_('Resize Up/Down'))
        return

# OK
    def keyOK(self):
        pass

#### Green
    def keyGreen(self):
        myIndex=self["menu"].getIndex()
        if self.currAction == self.doNothing:
            return
        elif self.currAction == self.doDelete:
            self.doDeleteAction(myIndex)
        elif self.currAction == self.doExport:
            self.doExportAction(myIndex)
        elif self.currAction == self.doImport:
            self.doImportFunc()
        self.EditedScreen = True

#### Green subprocedures

    def doDeleteAction(self, what):
        childAttributes=''
        for key, value in self.root[0][what].items():
            childAttributes += key + '=' + value + ' '
        printDEBUG('doDeleteAction <%s %s>\n' % (self.root[0][what].tag,childAttributes))
        self.root[0].remove(self.root[0][what])
            
        self.createWidgetsList()
        
    def doExportAction(self, what):
      
        printDEBUG('doExportAction')
        
        def SaveWidget(WidgetFile = None):
            if WidgetFile is not None:
                if not WidgetFile.endswith('.xml'):
                    WidgetFile += '.xml'
                WidgetPathName = path.dirname(self.ScreenFile).replace('allScreens','allWidgets')
                if not path.exists(WidgetPathName):
                    mkdir(WidgetPathName)
                printDEBUG("Writing %s/%s" % (WidgetPathName,WidgetFile))
                with open("%s/%s" % (WidgetPathName, WidgetFile), "w") as f:
                    f.write(ET.tostring(self.root[0][self["menu"].getIndex()]))

        myText=self.root[0][what].tag
        if 'name' in self.root[0][what].attrib:
            myText += '_' + self.root[0][what].attrib['name']
        if 'text' in self.root[0][what].attrib:
            myText += '_' + self.root[0][what].attrib['text']
        if 'render' in self.root[0][what].attrib:
            myText += '_' + self.root[0][what].attrib['render']
        if 'source' in self.root[0][what].attrib:
            myText += '_' + self.root[0][what].attrib['source']

        from Screens.VirtualKeyBoard import VirtualKeyBoard
        self.session.openWithCallback(SaveWidget, VirtualKeyBoard, title=(_("Enter filename")), text = myText.replace('.','-'))
        
    def doImportFunc(self):
        widgetlist = []
        for f in sorted(listdir(self.skin_base_dir + "allWidgets/"), key=str.lower):
            if f.endswith('.xml') and f.startswith('widget_'):
                friendly_name = f.replace("widget_", "")
                friendly_name = friendly_name.replace(".xml", "")
                friendly_name = friendly_name.replace("_", " ")
                widgetlist.append((friendly_name, f))
        if len(widgetlist) > 0:
            self.session.openWithCallback(self.doImportFuncRet, ChoiceBox, title = _("Select Widget:"), list = widgetlist)
            
    def doImportFuncRet(self, ret):
        if ret:
            if path.exists(self.skin_base_dir + "allWidgets/"+ret[1]):
                widgetRoot = ET.parse(self.skin_base_dir + "allWidgets/"+ret[1]).getroot()
                self.root[self.currentScreenID].insert(self["menu"].getIndex(),widgetRoot)
            self.createWidgetsList()
