from inits import PluginLanguageDomain , PluginLanguagePath
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext

def localeInit():
        gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))

def _(txt):
        t = gettext.dgettext(PluginLanguageDomain, txt)
        if t == txt:
                t = gettext.gettext(txt)
        return t

localeInit()
language.addCallback(localeInit)
