import csv
import os
import logging

from zope.app.component.hooks import getSite

from Acquisition import aq_inner

from Products.Archetypes.utils import addStatusMessage
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from collective.loremipsum import MessageFactory as _
from collective.loremipsum.utils import create_subobjects
from collective.loremipsum.config import OPTIONS

log = logging.getLogger(__name__)

class RegisterDummyUsers(BrowserView):
    """ """

    def __call__(self, **kw):
        """ """
        site = getSite()
        mdata = getToolByName(site, 'portal_memberdata')
        regtool = getToolByName(site, 'portal_registration')
        basedir = os.path.abspath(os.path.dirname(__file__))
        datadir = os.path.join(basedir, '../dummydata')
        file = open(datadir+'/memberdata.csv')
        reader = csv.reader(file)
        row_num = 0
        for row in reader:
            if row_num == 0:
                # We will use the headers in the first row as variable names to
                # store the user's details in portal_memberdata.
                dummy_fields = row
            else:   
                properties = {}
                for field in dummy_fields:
                    # Since we don't know what properties might be in
                    # portal_memberdata, for example postal_code or zipcode or
                    # zip_code, we make give each header a list of possible values
                    # separated by spaces.
                    fields = field.split(' ')
                    for f in fields:
                        if hasattr(mdata, f):
                            properties[f] = row[dummy_fields.index(field)]

                fullname = row[0] + ' ' + row[1] 
                username = self.sanitize(fullname.lower().replace(' ', '-'))
                properties['username'] = username 
                properties['fullname'] = fullname
                try:
                    # addMember() returns MemberData object
                    member = regtool.addMember(username, 'secret', properties=properties)
                except ValueError, e:
                    # Give user visual feedback what went wrong
                    IStatusMessage(self.request).add(_(u"Could not create the users. %s" % username) + unicode(e), "error") 
                    continue
                else:
                    log.info('Registered dummy user: %s' % fullname)
            row_num += 1

        IStatusMessage(self.request).add(_(u"Succesfully created %d users." % (row_num-1)), "info") 
        return self.request.RESPONSE.redirect('/'.join(self.context.getPhysicalPath()))

    def sanitize(self, str):
        for code, ascii in [('\xc3\xbc', 'ue'), 
                            ('\xc3\xb6', 'oe'),
                            ('\xc3\xa4', 'ae'), 
                            ('\xc3\xa7', 'c'),
                            ('\xc3\xa8', 'e'), 
                            ('\xc3\xa9', 'e'),
                            ('\xc3\xab', 'e'), 
                            ('\xc3\xaf', 'i'),
                            ('\xc5\x9e', 'S'), 
                            ('\xc5\x9f', 'e'),
                            ]:
            str = str.replace(code, ascii)
            str = str.decode('utf-8').encode('ascii', 'ignore')
        return str


class CreateDummyData(BrowserView):
    """ """

    def __call__(self, **kw):
        """ 
        type: string - The portal_type of the content type to create
        amount: integer - The amount of objects to create

        ul: bool - Add unordered lists.
        ol: bool - Add numbered lists.
        dl: bool - Add description lists.
        bq: bool - Add blockquotes.
        code: bool - Add code samples.
        link: bool - Add links.
        prude: bool - Prude version.
        headers: bool - Add headers.
        allcaps: bool - Use ALL CAPS.
        decorate: bool - Add bold, italic and marked text.

        publish: bool - Should the objects be published

        recurse: bool - Should objects be created recursively?

        parnum: integer - 
            The number of paragraphs to generate. (NOT USED)

        length: short, medium, long, verylong - 
            The average length of a paragraph (NOT USED)
        """
        request = self.request
        context = aq_inner(self.context)

        types = self.request.get('type')
        if isinstance(types, str):
            types = [types]

        # There are some formatting options that we want enabled by default. If
        # the user didn't specify them in the URL, we add them here.
        for key, default in OPTIONS.items():
            if not request.has_key(key):
                request.set(key, default)

        total = create_subobjects(context, request, 0, types)
        addStatusMessage(request, _('%d objects successfully created' % total))
        return request.RESPONSE.redirect('/'.join(context.getPhysicalPath()))


