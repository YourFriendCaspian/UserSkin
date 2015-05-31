from inits import UserSkinInfo, SkinPath
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from os import path

class UserSkin_About(Screen):
    skin = """
  <screen name="UserSkin_About" position="center,center" size="400,150" title="UserSkin info">
    <eLabel text="(c)2014/2015 by j00zek" position="0,15" size="370,50" font="Regular;28" halign="center" />
    <eLabel text="Based on AtileHD skin by schomi / plugin by VTi" position="0,55" size="400,30" font="Regular;18" halign="center" />
    <eLabel text="http://forum.xunil.pl" position="0,90" size="400,30" font="Regular;24" halign="center" />
    <widget name="skininfo" position="0,120" size="400,25" font="Regular;20" halign="center"/>
  </screen>
"""

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.cancel,
                "ok": self.keyOk,
            }, -2)
        self.setTitle(_("UserSkin %s") % UserSkinInfo)
        self['skininfo'] = Label("")
        if path.exists(SkinPath + 'skin.config'):
            with open(SkinPath + 'skin.config', "r") as f:
                for line in f:
                    if line.startswith('description='):
                        self['skininfo'].text = line.split('=')[1].replace('"','').replace("'","").strip()
                        break
                f.close()

    def keyOk(self):
        self.close()

    def cancel(self):
        self.close()
