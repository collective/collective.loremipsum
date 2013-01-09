import datetime
import logging
import loremipsum
import random
import transaction
import urllib
from StringIO import StringIO
from base64 import decodestring

from zope import component
from zope.globalrequest import getRequest
from zope.container.interfaces import INameChooser
from zope.schema import getFieldNames
from zope.schema import interfaces
from zope.schema.interfaces import WrongType

from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IDataManager
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import NOT_CHANGED
from z3c.form.interfaces import NO_VALUE

from plone.app.z3cform.wysiwyg.widget import IWysiwygWidget

from plone.autoform.interfaces import WIDGETS_KEY
from plone.dexterity import utils
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.uuid.interfaces import IUUID

from Acquisition import aq_base
from OFS.interfaces import IObjectManager
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interfaces import IATEvent
from Products.Archetypes.Widget import RichWidget
from Products.Archetypes.interfaces import field  as atfield
from Products.Archetypes.interfaces.base import IBaseContent 
from Products.Archetypes.interfaces.vocabulary import IVocabulary
from Products.Archetypes.utils import addStatusMessage
from Products.Archetypes.utils import shasattr
from Products.CMFCore.WorkflowCore import WorkflowException

try:
    HAS_USERANDGROUPSELECTIONWIDGET = True
    from Products.UserAndGroupSelectionWidget.z3cform.interfaces import \
                                                IUserAndGroupSelectionWidget
except:
    HAS_USERANDGROUPSELECTIONWIDGET = False
    
from collective.loremipsum import MessageFactory as _
from collective.loremipsum.config import BASE_URL, OPTIONS

log = logging.getLogger(__name__)

def create_subobjects(root, context, data, total=0):
    amount = int(data.get('amount', 3))
    types = data.get('portal_type')
    if types is None:
        base = aq_base(context)
        if IBaseContent.providedBy(base):
            types = []
            if hasattr(base, 'constrainTypesMode') and base.constrainTypesMode:
                types = context.locallyAllowedTypes
        elif IDexterityContent.providedBy(base):
            fti = component.getUtility(IDexterityFTI, name=context.portal_type)
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

    recurse = False
    if data.get('recurse', None) not in [None, '0', 'False', False]:
        depth = 0
        node = context
        while IUUID(node) != IUUID(root):
            depth += 1
            node = node.aq_parent

        if depth < data.get('recursion_depth'):
            recurse = True

    for portal_type in types:
        for n in range(0, amount):
            obj = create_object(context, portal_type, data)
            total += 1

            if not IObjectManager.providedBy(obj):
                continue

            if recurse:
                if not data.get('recurse_same_ptypes', False):
                    if shasattr(obj, 'getLocallyAllowedTypes'):
                        data['portal_type'] = \
                                list(obj.getLocallyAllowedTypes())
                    elif shasattr(obj, 'allowedContentTypes'):
                        data['portal_type'] = \
                                [t.id for t in obj.allowedContentTypes()]

                total = create_subobjects(root, obj, data, total)
    return total


def generate_unique_id(container, name, portal_type):
    name = name.lstrip('+@') or portal_type
    name = name.replace(' ', '-').replace('/', '-').lower()
    # for an existing name, append a number.
    # We should keep client's os.path.extsep (not ours), we assume it's '.'
    dot = name.rfind('.')
    if dot >= 0:
        suffix = name[dot:]
        name = name[:dot]
    else:
        suffix = ''

    n = name + suffix
    i = 1
    while n in container:
        i += 1
        n = name + '-' + str(i) + suffix
    # Make sure the name is valid.  We may have started with something bad.
    INameChooser(container).checkName(n, None)
    return n


def create_object(context, portal_type, data):
    """ """
    title = get_text_line()
    unique_id = generate_unique_id(context, title, portal_type)

    args = dict(id=unique_id)
    if portal_type in ['Image', 'File']:
        myfile = StringIO(decodestring('R0lGODlhAQABAPAAAPj8+AAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='))
        ext =  portal_type == 'Image' and 'gif' or 'dat'
        myfile.filename = '.'.join((get_text_line().split(' ')[-1], ext))
        args.update({'file':myfile})

    new_id= context.invokeFactory(portal_type, **args)
    obj = context[new_id]

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

    # set same language as parent
    obj.setLanguage(context.Language())
    obj.reindexObject()
    log.info('%s Object created' % obj.portal_type)
    if data.get('commit'):
        transaction.commit()
    return obj

def get_text_line():
    return loremipsum.Generator().generate_sentence()[2]

def get_text_paragraph():
    return [p[2] for p in loremipsum.Generator().generate_paragraphs(1)][0]

def get_rich_text(data):
    url =  BASE_URL + '/3/short'
    for key, default in OPTIONS.items():
        if key in data.get('formatting', []):
            url += '/%s' % key
    return urllib.urlopen(url).read().decode('utf-8')

def get_dexterity_schemas(context=None, portal_type=None):
    """ Utility method to get all schemas for a dexterity object.
        
        IMPORTANT: Either context or portal_type must be passed in, NOT BOTH.
        The idea is that for edit forms context is passed in and for add forms 
        where we don't have a valid context we pass in portal_type.

        This builds on getAdditionalSchemata, which works the same way.
    """
    if context is not None:
        portal_type = context.portal_type

    fti = component.getUtility(IDexterityFTI, name=portal_type)
    schemas = [fti.lookupSchema()]
    for behavior_schema in \
            utils.getAdditionalSchemata(context=context, portal_type=portal_type):
        if behavior_schema is not None:
            schemas.append(behavior_schema)
    return schemas


def get_dummy_dexterity_value(obj, widget, data):
    value = None
    field = widget.field
    catalog = getToolByName(obj, 'portal_catalog')
    if interfaces.IChoice.providedBy(field):
        if shasattr(field, 'vocabulary') and field.vocabulary:
            vocabulary = field.vocabulary
        elif shasattr(field, 'vocabularyName') and field.vocabularyName:
            factory = component.getUtility(
                            interfaces.IVocabularyFactory, 
                            field.vocabularyName)
            vocabulary = factory(obj)
        else:
            return 

        if interfaces.IContextSourceBinder.providedBy(vocabulary):
            criteria = vocabulary.selectable_filter.criteria
            results = catalog(**criteria)
            if not len(results):
                return 
            value = results[random.randint(0, len(results)-1)].getObject()
        else:
            if interfaces.ITreeVocabulary.providedBy(vocabulary):
                # Can't yet deal with tree vocabs
                return
            index  = random.randint(0, len(vocabulary)-1)
            value = vocabulary._terms[index].value

    elif interfaces.IBool.providedBy(field):
        value = random.randint(0,1) and True or False

    elif interfaces.ITextLine.providedBy(field):
        if HAS_USERANDGROUPSELECTIONWIDGET and \
                IUserAndGroupSelectionWidget.providedBy(widget):
            mtool = getToolByName(obj, 'portal_membership')
            mids = mtool.listMemberIds()
            value = mids[random.randint(0, len(mids)-1)]
        else:
            length = getattr(field, 'max_length', None) 
            value = unicode(get_text_line()[:length])

    elif interfaces.IText.providedBy(field):
        if IWysiwygWidget.providedBy(widget):
            value = unicode(get_rich_text(data))
        else:
            value = unicode(get_text_paragraph())

    elif interfaces.IDatetime.providedBy(field):
        days = random.random()*10 * (random.randint(-1,1) or 1)
        value = datetime.datetime.now() + datetime.timedelta(days,0)

    elif interfaces.IDate.providedBy(field):
        days = random.random()*10 * (random.randint(-1,1) or 1)
        value = datetime.datetime.now() + datetime.timedelta(days,0)

    return value


def populate_dexterity_type(obj, data):
    request = getRequest()
    for schema in get_dexterity_schemas(context=obj):
        for name in getFieldNames(schema):
            field = schema[name]
            autoform_widgets = schema.queryTaggedValue(WIDGETS_KEY, default={})
            if name in autoform_widgets:
                widgetclass = utils.resolveDottedName(autoform_widgets[name])
                widget = widgetclass(field, request)
            else:
                widget = component.getMultiAdapter((field, request), IFieldWidget)

            widget.context = obj
            widget.ignoreRequest = True
            widget.update()
            value = widget.value

            if not value or value in [NOT_CHANGED, NO_VALUE] or \
                    not IDataConverter(widget).toFieldValue(widget.value):
                value = get_dummy_dexterity_value(obj, widget, data)

            if value:
                dm = component.getMultiAdapter((obj, field), IDataManager)
                try:
                    dm.set(value)
                except WrongType:
                    value = IDataConverter(widget).toFieldValue(value)
                    dm.set(value)


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
