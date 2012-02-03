import logging
from zope import schema
from zope import interface

from z3c.form import field
from z3c.form import form
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from Acquisition import aq_inner

from plone.z3cform.layout import FormWrapper
from plone.z3cform.fieldsets.extensible import ExtensibleForm
from Products.Archetypes.utils import addStatusMessage
from Products.Archetypes.utils import shasattr

from collective.loremipsum import MessageFactory as _
from collective.loremipsum.utils import create_subobjects

log = logging.getLogger(__name__)

formatting_vocabulary = schema.vocabulary.SimpleVocabulary.fromItems([
        ("Add unordered lists <ul>", 'ul'),
        ("Add numbered lists <ol>", 'ol'),
        ("Add description lists <dl>", 'dl'),
        ("Add blockquotes <bq>", 'bq'),
        ("Add code samples <code>", 'code'),
        ("Add links <link>", 'link'),
        ("Prude version (removes legitimate latin words like 'sex')", 'prude'),
        ("Add headers", 'headers'),
        ("Use ALL CAPS", 'allcaps'),
        ("Add bold, italic and marked text", 'decorate'),
    ])

class IPopulateFormSchema(interface.Interface):
    """ """
    portal_type = schema.List(
            title=_(u"Item Type"),
            description=_(u"Choose the types of objects you'd like to "
                        u"create dummies of. The column on the right contains "
                        u"the types that will be created, which is by default "
                        u"all the types allowed in this folder."),
            value_type=schema.Choice(
                vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"),
            )

    amount = schema.Int(
            title=_(u"Amount"),
            description=_(u"Choose the amount of objects you'd like to be "
                        u"created for each type chosen above. "
                        u"The default is 3."),
            default=3,
            )

    recurse = schema.Bool(
            title=_(u"Recurse"),
            description=_(u"Should objects be created recursively?"),
            )

    publish = schema.Bool(
            title=_(u"Publish objects"),
            description=_(u"Should newly created objects be published?"),
            )

    formatting = schema.List(
            title=_(u"Text Formatting"),
            description=_(u"Choose from the formatting options for the lorem "
                        u"ipsum dummy text."),
            default=['ul', 'ol', 'dl', 'bq', 'code', 
                     'link', 'headers', 'decorate'],
            required=False,
            value_type=schema.Choice(
                vocabulary=formatting_vocabulary),
            )

class IPopulateFormButtons(interface.Interface):
    """ """
    create = button.Button(title=_(u"Create the dummy content"))


class PopulateForm(ExtensibleForm, form.Form):
    ignoreContext = True
    fields = field.Fields(IPopulateFormSchema)
    buttons = button.Buttons(IPopulateFormButtons)

    def updateFields(self):
        super(PopulateForm, self).updateFields()
        self.fields['formatting'].widgetFactory = CheckBoxFieldWidget
        context = aq_inner(self.context)
        if shasattr(context, 'getLocallyAllowedTypes'):
            self.fields['portal_type'].field.default = \
                                list(context.getLocallyAllowedTypes())
        elif shasattr(context, 'allowedContentTypes'):
            self.fields['portal_type'].field.default = \
                                [t.id for t in context.allowedContentTypes()]
            
    @button.handler(IPopulateFormButtons['create'])
    def create(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = '\n'.join([error.error.__str__() for error in errors])
            return 

        context = aq_inner(self.context)
        total = create_subobjects(context, data, 0)
        addStatusMessage(
                self.request, 
                'Successfully created %d dummy objects.' % total, 
                type='info')
        self.request.response.redirect(self.context.REQUEST.get('URL'))


class Populate(FormWrapper):
    """ """
    form = PopulateForm

