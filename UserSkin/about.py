from inits import UserSkinInfo
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText

class UserSkin_About(Screen):
    skin = """
  <screen name="UserSkin_About" position="center,center" size="400,120" title="UserSkin info">
    <eLabel text="(c)2014/2015 by j00zek" position="0,15" size="370,50" font="Regular;28" halign="center" />
    <eLabel text="Based on AtileHD skin by schomi / plugin by VTi" position="0,55" size="400,30" font="Regular;18" halign="center" />
    <eLabel text="http://forum.xunil.pl" position="0,90" size="400,30" font="Regular;24" halign="center" />
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

    def keyOk(self):
        self.close()

    def cancel(self):
        self.close()
