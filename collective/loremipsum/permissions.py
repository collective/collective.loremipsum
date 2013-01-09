# -*- coding: utf-8 -*-

from AccessControl.SecurityInfo import ModuleSecurityInfo

PROJECTNAME = 'collective.loremipsum'

security = ModuleSecurityInfo(PROJECTNAME)

security.declarePublic('CanPopulate')
CanPopulate = PROJECTNAME + ': Can Populate'
