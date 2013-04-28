from collective.loremipsum.interfaces import IProductLayer
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
from zope.configuration import xmlconfig
from zope.interface import alsoProvides


class LoremIpsumFixture(PloneSandboxLayer):
    """ """

    def setUpZope(self, app, configurationContext):
        import collective.loremipsum
        xmlconfig.file('configure.zcml', collective.loremipsum,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.loremipsum:default')
        # Manually enable the xmpp.core browserlayer
        alsoProvides(portal.REQUEST, IProductLayer)


LOREMIPSUM_FIXTURE = LoremIpsumFixture()

LOREMIPSUM_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(LOREMIPSUM_FIXTURE, z2.ZSERVER_FIXTURE),
    name="collective.xmpp.chatLayer:Functional"
)
