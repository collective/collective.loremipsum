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
from collective.loremipsum.fakeimagegetter import DEFAULT_IMAGE_GETTER


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
            title=_(u"Should objects be created recursively?"),
            description=_(u'description_recurse',
                    default= u"If the objects added are containers, then new "
                        u"objects will be created inside them and so forth. "
                        u"The types of objects created inside a container are "
                        u"determined by the allowable types inside that "
                        u"container."),
            )

    recursion_depth = schema.Int(
            title=_(u"Recursion Depth"),
            description=_(u"If objects are created recursively, how many levels"
                          u" deep should they be created?"),
            required=True,
            default=3,
            )

    recurse_same_ptypes = schema.Bool(
            title=_(u"Use the same portal types selected above?"),
            description=_(u'description_recurse',
                    default=u"Generate sub-objects using only content types declared into 'Item Type'."),
            default=True,
            )

    generate_images = schema.Bool(
            title=_(u"Generate fake images' content?"),
            description=_(u"Check this box to get random fake images "
                    u"for all the items with a field named 'image'. ARCHETYPES ONLY"),
            default=False,
            required=False,
            )

    generate_images_service = schema.Choice(
            title=_(u"Image service"),
            description=_(u"Choose which service to use to generate images"),
            vocabulary="collective.loremipsum.fakeimagegetters",
            default=DEFAULT_IMAGE_GETTER,
            required=False,
            )

    generate_images_params = schema.TextLine(
            title=_(u"Image parameters"),
            description=_(u"Column ';' separated parameters for the image service. "
                          u"Check respective websites for available parameters. "
                          u"Default 'text' is the title of the generated object."),
            default=u"size=300x200; category=sports;",
            required=False,
            )

    subjects = schema.Text(
            title=_(u"Subjects"),
            description=_(u"Line separated subjects. If none provided a default set will be used."),
            required=False,
            )

    publish = schema.Bool(
            title=_(u"Publish objects"),
            description=_(u"Should newly created objects be published?"),
            required=False,
            )

    commit = schema.Bool(
            title=_(u"Commit between objects"),
            description=_(u"Check this box if the transaction should be "
                u"committed each time an object is created. This will take more "
                u"time but might be necessary, for example if you have default "
                u"values that depend on previous objects being catalogued."),
            required=False,
            )

    formatting = schema.List(
            title=_(u"Rich Text Formatting"),
            description=_(u"Choose from the formatting options for "
                        u"the lorem ipsum dummy text. This only "
                        u"applies to RichText fields."),
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
        total = create_subobjects(context, context, data, 0)
        addStatusMessage(
                self.request,
                'Successfully created %d dummy objects.' % total,
                type='info')
        self.request.response.redirect(self.context.REQUEST.get('URL'))


class Populate(FormWrapper):
    """ """
    form = PopulateForm
