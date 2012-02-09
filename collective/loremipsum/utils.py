import datetime
import logging
import random
import time
import urllib
from htmllaundry import StripMarkup
from StringIO import StringIO
from base64 import decodestring

from zope.container.interfaces import INameChooser
from zope.component import getMultiAdapter, getUtility
from zope.schema import interfaces

from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.app.z3cform.wysiwyg.widget import IWysiwygWidget

from Acquisition import aq_base
from DateTime import DateTime
from zExceptions import BadRequest

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interfaces import IATEvent
from Products.Archetypes.Widget import RichWidget
from Products.Archetypes.interfaces import field  as atfield
from Products.Archetypes.interfaces.base import IBaseContent 
from Products.Archetypes.interfaces.vocabulary import IVocabulary
from Products.Archetypes.utils import addStatusMessage
from Products.Archetypes.utils import shasattr
from Products.CMFCore.WorkflowCore import WorkflowException

from collective.loremipsum import MessageFactory as _
from collective.loremipsum.config import BASE_URL, OPTIONS

log = logging.getLogger(__name__)

def create_subobjects(context, data, total=0):
    amount = int(data.get('amount', 3))
    types = data.get('portal_type')
    if types is None:
        base = aq_base(context)
        if IBaseContent.providedBy(base):
            types = []
            if hasattr(base, 'constrainTypesMode') and base.constrainTypesMode:
                types = context.locallyAllowedTypes
        elif IDexterityContent.providedBy(base):
            fti = getUtility(IDexterityFTI, name=context.portal_type)
            types = fti.filter_content_types and fti.allowed_content_types
            if not types:
                msg = _('Either restrict the addable types in this folder or ' \
                        'provide a type argument.')
                addStatusMessage(context.request, msg)
                return total
        else:
            msg = _("The context doesn't provide IBaseContent or "
                    "IDexterityContent. It might be a Plone Site object, "
                    "but either way, I haven't gotten around to dealing with "
                    "it. Why don't you jump in and help?")
            addStatusMessage(context.request, msg)
            return total

    for portal_type in types:
        if portal_type in ['File', 'Folder']:
            continue
            
        for n in range(0, amount):
            obj = create_object(context, portal_type, data)
            total += 1
            if data.get('recurse', None) not in [None, '0', 'False', False]:
                total = create_subobjects(obj, data, total)
    return total


def create_object(context, portal_type, data):
    """ """
    url = BASE_URL + '/1/short'
    response = urllib.urlopen(url).read()
    title = StripMarkup(response.decode('utf-8')).split('.')[1]
    id = INameChooser(context).chooseName(title, context)
    myfile = None
    if portal_type == 'Image':
        myfile = StringIO(decodestring('R0lGODlhAQABAPAAAPj8+AAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='))
        myfile.filename = '.'.join((get_text_line().split(' ')[-1], 'gif'))
        args = dict(id=id, file=myfile)
    else:
        args = dict(id=id)
    try:
        id = context.invokeFactory(portal_type, **args)
    except BadRequest:
        id += '%f' % time.time()
        id = context.invokeFactory(portal_type, **args)
        
    obj = context[id]

    if IDexterityContent.providedBy(obj):
        if shasattr(obj, 'title'):
            obj.title = title
            populate_dexterity_type(obj, data)
    else:
        obj.setTitle(title)
        populate_archetype(obj, data)

    if data.get('publish', True):
        wftool = getToolByName(context, 'portal_workflow')
        try:
            wftool.doActionFor(obj, 'publish')
        except WorkflowException, e:
            log.warn(e)

    obj.reindexObject()
    log.info('%s Object created' % obj.portal_type)
    return obj


def get_text_line():
    url = BASE_URL + '/1/short'
    try:
        response = urllib.urlopen(url).read()
    except IOError, e:
        response = str(e)
    return StripMarkup(response.decode('utf-8')).split('.')[1]


def get_text_paragraph():
    url =  BASE_URL + '/1/short'
    try:
        response = urllib.urlopen(url).read()
    except IOError, e:
        response = str(e)
    return StripMarkup(response.decode('utf-8'))


def get_rich_text(data):
    url =  BASE_URL + '/3/short'
    for key, default in OPTIONS.items():
        if data.get(key):
            url += '/%s' % key
    return urllib.urlopen(url).read().decode('utf-8')


def populate_dexterity_type(obj, data):
    view = getMultiAdapter((obj, obj.request), name="edit")
    view.update()
    view.form_instance.render()
    fields = view.form_instance.fields._data_values

    for i in range(0, len(fields)):
        field = fields[i].field 
        name = field.__name__

        if name == 'title':
            continue

        if interfaces.IChoice.providedBy(field):
            if shasattr(field, 'vocabulary') and field.vocabulary:
                vocabulary = field.vocabulary
            elif shasattr(field, 'vocabularyName') and field.vocabularyName:
                factory = getUtility(
                                interfaces.IVocabularyFactory, 
                                field.vocabularyName)
                vocabulary = factory(obj)
            else:
                continue
            index  = random.randint(0, len(vocabulary)-1)
            value = vocabulary._terms[index].value

        elif interfaces.ITextLine.providedBy(field):
            value = get_text_line()

        elif interfaces.IText.providedBy(field):
            widget = view.form_instance.widgets._data_values[i]

            if IWysiwygWidget.providedBy(widget):
                value = get_rich_text(data) 
            else:
                value = get_text_paragraph() 

        elif interfaces.IDatetime.providedBy(field):
            days = random.random()*10 * (random.randint(-1,1) or 1)
            value = datetime.datetime.now() + datetime.timedelta(days,0)

        elif interfaces.IDate.providedBy(field):
            days = random.random()*10 * (random.randint(-1,1) or 1)
            value = datetime.datetime.now() + datetime.timedelta(days,0)

        else:
            continue
        field.set(obj, value)


def populate_archetype(obj, data):
    fields = obj.Schema().fields()

    for field in fields:
        name = field.__name__
        if name in ['title', 'id']:
            continue

        if shasattr(field, 'vocabulary') and IVocabulary.providedBy(field.vocabulary):
            vocab = field.vocabulary.getVocabularyDict(obj)
            value = vocab.keys()[random.randint(0, len(vocab.keys())-1)]
            
        elif atfield.IStringField.providedBy(field):
            validators = [v[0].name for v in field.validators]
            if 'isURL' in validators:
                value = 'http://en.wikipedia.com/wiki/Lorem_ipsum'
            elif 'isEmail' in validators:
                value = 'loremipsum@mail.com'
            else:
                value = get_text_line()

        elif atfield.ITextField.providedBy(field):
            widget = field.widget
            if isinstance(widget, RichWidget):
                value = get_rich_text(data) 
            else:
                value = get_text_paragraph() 

        elif atfield.IBooleanField.providedBy(field):
            value = random.randint(0,1) and True or False
        else:
            continue

        field.set(obj, value)

    if IATEvent.providedBy(obj):
        days = random.random()*20 * (random.randint(-1,1) or 1)
        value = DateTime() + days
        obj.setStartDate(value)
        obj.setEndDate(value+random.random()*3)


