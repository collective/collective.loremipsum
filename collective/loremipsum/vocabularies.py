# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.component import getAllUtilitiesRegisteredFor
from zope.schema import vocabulary
try:
    # plone 3
    from zope.app.schema.vocabulary import IVocabularyFactory
except:
    # plone 4
    from zope.schema.interfaces import IVocabularyFactory

from collective.loremipsum.fakeimagegetter import IFakeImageGetter


createTerm = vocabulary.SimpleVocabulary.createTerm


class BaseVocabulary(object):
    implements(IVocabularyFactory)

    _terms = []

    def __call__(self, context):
        terms = [createTerm(term[0], term[0], term[1])
                 for term in self._terms]
        return vocabulary.SimpleVocabulary(terms)


class FakeImageGetters(BaseVocabulary):

    @property
    def _terms(self):
        utilities = getAllUtilitiesRegisteredFor(IFakeImageGetter)
        for getter in utilities:
            yield (getter.name, getter.name)
