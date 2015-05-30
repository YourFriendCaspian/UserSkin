# -*- coding: utf-8 -*-
UserSkinInfo='@j00zek 30/05/2015'

#stale
PluginName = 'UserSkin'
PluginGroup = 'Extensions'

#Paths
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
PluginFolder = PluginName
PluginLanguageDomain = PluginName
PluginLanguagePath = '%s/%s/locale' % (PluginGroup,PluginFolder)
PluginPath = resolveFilename(SCOPE_PLUGINS, '%s/%s/' %(PluginGroup,PluginFolder))

#DEBUG
myDEBUG=True
myDEBUGfile = '/tmp/%s.log' % PluginName
