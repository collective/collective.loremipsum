import urllib
import string
from PIL import Image
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from zope import interface


class IFakeImageGetter(interface.Interface):
    """ utility for getting fake images
    """


class FakeImageGetter(object):
    interface.implements(IFakeImageGetter)

    name = ''
    url_template = ''
    about_url = ''
    defaults = {'size': '300x200'}

    def get(self, **kwargs):
        """ get an image
            `kwargs` usually contains
                size, text
        """
        return self._get(**kwargs)

    def _get(self, **kwargs):
        data = self._get_params(**kwargs)
        url = self.get_url(**data)
        content = urllib.urlopen(url).read()
        # check if we got a real content and not some html error page
        try:
            Image.open(StringIO(content))
        except IOError:
            return None
        return content

    def _get_params(self, **kwargs):
        data = kwargs.copy()
        for k, v in self.defaults.items():
            if not data.get(k):
                data[k] = v
        params = data.pop('params')
        if params:
            for param in params.split(';'):
                try:
                    k, v = param.split('=')
                    data[k.strip()] = v.strip()
                except:
                    # drop param if broken
                    pass
        # clean text
        # some service breaks if puntuaction is found in text
        # http://stackoverflow.com/questions/265960/
        # best-way-to-strip-punctuation-from-a-string-in-python
        if 'text' in data.keys():
            trans_table = string.maketrans(" ", " ")
            data['text'] = data['text'].translate(trans_table,
                                                  string.punctuation)
        return data

    def get_url(self, **kwargs):
        url = self.url_template % kwargs
        return url


class FakeimgPL(FakeImageGetter):

    name = 'fakeimg.pl'
    url_template = 'http://fakeimg.pl/%(size)s/?text=%(text)s'
    about_url = 'http://fakeimg.pl/'


class PlaceHold(FakeImageGetter):

    name = 'placehold.it'
    url_template = 'http://placehold.it/%(size)s&text=%(text)s'
    about_url = 'http://placehold.it/'


class PlaceKitten(FakeImageGetter):

    name = 'placekitten.com'
    url_template = 'http://placekitten.com/%(width)s/%(height)s'
    about_url = 'http://placekitten.com/'

    def get_url(self, **kwargs):
        data = kwargs.copy()
        if 'size' in kwargs.keys():
            data['width'], data['height'] = kwargs['size'].split('x')
        url = self.url_template % data
        return url


class LoremPixel(PlaceKitten):

    name = 'lorempixel.com'
    url_template = 'http://lorempixel.com/%(width)s/%(height)s/%(category)s/%(text)s/'
    about_url = 'http://lorempixel.com'
    defaults = {'category': 'sports'}


fakeimgpl = FakeimgPL()
placehold = PlaceHold()
placekitten = PlaceKitten()
lorempixel = LoremPixel()

DEFAULT_IMAGE_GETTER = 'lorempixel.com'
