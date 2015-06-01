# -*- coding: utf-8 -*-

# UserSkin, based on AtileHD concept
#
# maintainer: <schomi@vuplus-support.org> / <plnick@vuplus-support.org>
#
# extension for openpli, all skins, descriptions, bar selections and other @j00zek 2014/2015
# Uszanuj czyj¹œ pracê i NIE przyw³aszczaj sobie autorstwa!

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.

from debug import printDEBUG
from inits import *
from translate import _

from Components.ActionMap import ActionMap

from Components.config import *
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import *
from Tools.LoadPixmap import LoadPixmap
from Tools import Notifications
from os import listdir, remove, rename, system, path
import shutil
import re
        
def Plugins(**kwargs):
    return [PluginDescriptor(name=_("UserSkin Setup"), description=_("Personalize your Skin"), where = PluginDescriptor.WHERE_MENU, fnc=menu)]

def menu(menuid, **kwargs):
    if menuid == "vtimain" or menuid == "system":
        return [(_("Setup - UserSkin"), main, "UserSkin_Menu", 40)]
    return []

def main(session, **kwargs):
    printDEBUG("Opening Menu ...")
    session.open(UserSkin_Menu)

class UserSkin_Menu(Screen):
        skin = """
<screen position="center,center" size="560,260">
        <widget source="list" render="Listbox" position="0,0" size="560,360" scrollbarMode="showOnDemand">
                <convert type="TemplatedMultiContent">
                        {"template": [
                                MultiContentEntryPixmapAlphaTest(pos = (12, 4), size = (32, 32), png = 0),
                                MultiContentEntryText(pos = (58, 5), size = (440, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),
                                ],
                                "fonts": [gFont("Regular", 22)],
                                "itemHeight": 40
                        }
                </convert>
        </widget>
</screen>"""

        def __init__(self, session):
                Screen.__init__(self, session)
                self.setup_title = _("UserSkinMenu")
                Screen.setTitle(self, self.setup_title)
                self["list"] = List()
                self["setupActions"] = ActionMap(["SetupActions", "MenuActions"],
                {
                        "cancel": self.quit,
                        "ok": self.openSelected,
                        "menu": self.quit,
                }, -2)
                self.setTitle(_("UserSkin menu %s") % UserSkinInfo)
                self.createsetup()

        def createsetup(self):
                l = [
                    (self.buildListEntry(_("Skin personalization"), "config.png",'config')),
                    (self.buildListEntry(_("Download addons"), "download.png",'getaddons')),
                    (self.buildListEntry(_("Delete addons"), "remove.png",'delete_addons')),
                    (self.buildListEntry(_("Update main skin"), "download.png",'getskin')),
                    (self.buildListEntry(_("Update plugin"), "download.png",'getplugin')),
                    (self.buildListEntry(_("About"), "about.png",'about')),
                ]
                self["list"].list = l

        def buildListEntry(self, description, image, optionname):
                try:
                        pixmap = LoadPixmap(SkinPath + "UserSkinpics/" + image)
                except:
                        pixmap = None
                if pixmap == None:
                        pixmap = LoadPixmap(cached=True, path="%spic/%s" % (PluginPath, image));
                return((pixmap, description, optionname))

        def refresh(self):
            index = self["list"].getIndex()
            self.createsetup()
            if index is not None and len(self["list"].list) > index:
                self["list"].setIndex(index)
            else:
                self["list"].setIndex(0)

        def openSelected(self):
            selected = str(self["list"].getCurrent()[2])
            if selected == 'about':
                from about import UserSkin_About
                self.session.openWithCallback(self.refresh,UserSkin_About)
                return
            elif selected == 'config':
                from skinconfig import UserSkin_Config
                self.session.openWithCallback(self.quit,UserSkin_Config)
                return
            elif selected == 'getaddons':
                from translatedconsole import myMenu
                self.session.openWithCallback(self.refresh, myMenu, MenuFolder = '%sscripts' % PluginPath, MenuFile = '_Getaddons')
                return
            elif selected == 'delete_addons':
                from translatedconsole import myMenu
                self.session.openWithCallback(self.refresh, myMenu, MenuFolder = '%sscripts' % PluginPath, MenuFile = '_Deleteaddons')
                return
            elif selected == 'getskin':
                def goUpdate(ret):
                    if ret is True:
                        from translatedconsole import UserSkinconsole
                        self.session.openWithCallback(self.refresh, UserSkinconsole, title = _("Updating skin"), cmdlist = [ '%sscripts/SkinUpdate.sh %s' % (PluginPath,SkinPath) ])
                    return
                self.session.openWithCallback(goUpdate, MessageBox,_("Do you want to update skin?"),  type = MessageBox.TYPE_YESNO, timeout = 10)
                return
            elif selected == 'getplugin':
                def goUpdate(ret):
                    if ret is True:
                        from translatedconsole import UserSkinconsole
                        self.session.openWithCallback(self.refresh, UserSkinconsole, title = _("Updating plugin"), cmdlist = [ '%sscripts/UserSkinUpdate.sh' % PluginPath ])
                    return
                self.session.openWithCallback(goUpdate, MessageBox,_("Do you want to update plugin?"),  type = MessageBox.TYPE_YESNO, timeout = 10)
                return

        def quit(self):
                self.close()
