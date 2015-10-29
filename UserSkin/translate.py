from inits import PluginLanguagePath
try:
    from os import path
    if path.exists(PluginLanguagePath):
        raise ValueError('a hack :)')
    from Components.LanguageGOS import gosgettext as _
except:
    from inits import PluginLanguageDomain
    from Components.Language import language
    import gettext
    from os import environ

    def localeInit():
        lang = language.getLanguage()[:2]
        environ["LANGUAGE"] = lang
        gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)

    def _(txt):
        t = gettext.dgettext(PluginLanguageDomain, txt)
        if t == txt:
                t = gettext.gettext(txt)
        return t

    localeInit()
    language.addCallback(localeInit)
