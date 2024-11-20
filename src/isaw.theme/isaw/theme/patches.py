from cgi import escape
from xml.sax.saxutils import quoteattr

from OFS.Image import Image
from Products.Archetypes.Field import ImageField
from Products.PluginIndexes.UUIDIndex.UUIDIndex import UUIDIndex
#from Products.TinyMCE.utility import TinyMCE
from plone.namedfile.scaling import ImageScale
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from zope.globalrequest import getRequest


_marker = object()

# Monkey-patch the TinyMCE utility to return a wildcard allowing all
# tags and attributes, so sanitization happens on save only (we hope).
#TinyMCE.getValidElements = lambda self: {'*': ['*']}
### aceglie TinyMCE no longer used in plone5.2


def allow_not_uuid():
    UUIDIndex.query_options = tuple(UUIDIndex.query_options) + ('not',)


def _wcag_tag(self, instance, scale=None, height=None, width=None, alt=None,
              css_class=None, title=None, **kwargs):
    """"Accept title as parameter, but do not use in img tag, per WCAG"""
    image = self.getScale(instance, scale=scale)
    if image:
        img_width, img_height = self.getSize(instance, scale=scale)
    else:
        img_height = 0
        img_width = 0

    if height is None:
        height = img_height
    if width is None:
        width = img_width

    url = instance.absolute_url()
    if scale:
        url += '/' + self.getScaleName(scale)
    else:
        url += '/' + self.getName()

    if not alt:
        alt = instance.Title()

    values = {'src': url,
              'alt': escape(alt, quote=True),
              'height': height,
              'width': width,
              }

    result = '<img src="%(src)s" alt="%(alt)s" '\
                'height="%(height)s" width="%(width)s"' % values

    if css_class is not None:
        result = '%s class="%s"' % (result, css_class)

    for key, value in kwargs.items():
        if value:
            result = '%s %s="%s"' % (result, key, value)

    return '%s />' % result


def img_tag_no_title():
    ImageField.tag = _wcag_tag


def _wcag_ofs_tag(self, height=None, width=None, alt=None,
        scale=0, xscale=0, yscale=0, css_class=None, title=None, **args):

    if height is None: height=self.height
    if width is None:  width=self.width

    xdelta = xscale or scale
    ydelta = yscale or scale

    if xdelta and width:
        width =  str(int(round(int(width) * xdelta)))
    if ydelta and height:
        height = str(int(round(int(height) * ydelta)))

    result='<img src="%s"' % (self.absolute_url())

    if alt is None:
        alt=getattr(self, 'alt', '')
    result = '%s alt="%s"' % (result, escape(alt, 1))

    if height:
        result = '%s height="%s"' % (result, height)

    if width:
        result = '%s width="%s"' % (result, width)

    if css_class is not None:
        result = '%s class="%s"' % (result, css_class)

    for key in args.keys():
        value = args.get(key)
        if value:
            result = '%s %s="%s"' % (result, key, value)

    return '%s />' % result


def ofs_img_tag_no_title():
    Image.tag = _wcag_ofs_tag


def _wcag_named_file_image_tag(self, height=_marker, width=_marker, alt=_marker,
        css_class=None, title=_marker, **kwargs):
    """Create a tag including scale
    """
    if height is _marker:
        height = getattr(self, 'height', self.data._height)
    if width is _marker:
        width = getattr(self, 'width', self.data._width)

    if alt is _marker:
        alt = getattr(self.context, 'alt', '')

    values = [
        ('src', self.url),
        ('alt', alt),
        ('height', height),
        ('width', width),
        ('class', css_class),
    ]
    values.extend(kwargs.items())

    parts = ['<img']
    for k, v in values:
        if v is None:
            continue
        if isinstance(v, int):
            v = str(v)
        elif isinstance(v, str):
            v = unicode(v, 'utf8')
        parts.append(u'{0}={1}'.format(k, quoteattr(v)))
    parts.append('/>')

    return u' '.join(parts)


def named_file_image_tag():
    ImageScale.tag =  _wcag_named_file_image_tag


def _fixed_image_scale_make(self, info):
    request = getRequest()
    alsoProvides(request, IDisableCSRFProtection)
    return self._orig_make(info)

def image_csrf_fix():
    from plone.app.imaging.scaling import ImageScaling

    if getattr(ImageScaling, '_orig_make', None) is None:
        ImageScaling._orig_make = ImageScaling.make
        ImageScaling.make = _fixed_image_scale_make
