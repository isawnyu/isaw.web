from Acquisition import aq_acquire, aq_parent
from zope.interface import implementer

from cgi import escape
from urlparse import urljoin
from urlparse import urlsplit

from plone.outputfilters.interfaces import IFilter
from plone.outputfilters.filters.resolveuid_and_caption import (
    ResolveUIDAndCaptionFilter,
    resolveuid_re,
)


@implementer(IFilter)
class WCAGResolveUIDAndCaptionFilter(ResolveUIDAndCaptionFilter):
    """ Parser to convert UUID links and captioned images """

    def unknown_starttag(self, tag, attrs):
        """Get rid of title attribute, and use caption attribute instead
        """
        if tag in ['a', 'img', 'area']:
            # Only do something if tag is a link, image, or image map area.

            attributes = dict(attrs)
            if tag == 'a':
                self.in_link = True
            if (tag == 'a' or tag == 'area') and 'href' in attributes:
                href = attributes['href']
                scheme = urlsplit(href)[0]
                if not scheme and not href.startswith('/') \
                        and not href.startswith('mailto<') \
                        and not href.startswith('#'):
                    obj, subpath, appendix = self.resolve_link(href)
                    if obj is not None:
                        href = obj.absolute_url()
                        if subpath:
                            href += '/' + subpath
                        href += appendix
                    elif resolveuid_re.match(href) is None:
                        # absolutize relative URIs; this text isn't necessarily
                        # being rendered in the context where it was stored
                        relative_root = self.context
                        if not getattr(
                            self.context, 'isPrincipiaFolderish', False):
                            relative_root = aq_parent(self.context)
                        actual_url = relative_root.absolute_url()
                        href = urljoin(actual_url + '/', subpath) + appendix
                    attributes['href'] = href
                    attrs = attributes.iteritems()
            elif tag == 'img':
                src = attributes.get('src', '')
                image, fullimage, src, description = self.resolve_image(src)
                attributes["src"] = src
                # use title to get caption, if any
                caption = attributes.get('title', '')
                # no title attribute for images
                if 'title' in attributes:
                    del attributes['title']
                # Check if the image needs to be captioned
                if (self.captioned_images and image is not None and caption
                    and 'captioned' in attributes.get('class', '').split(' ')):
                    self.handle_captioned_image(attributes, image, fullimage,
                                                caption)
                    return True
                if fullimage is not None:
                    # Check to see if the alt / title tags need setting
                    title = aq_acquire(fullimage, 'Title')()
                    if 'alt' not in attributes:
                        attributes['alt'] = description or title
                    attrs = attributes.iteritems()
                else:
                    # no caption, but we want same template
                    strattrs = "".join([' %s="%s"'
                                        % (key, escape(value, quote=True))
                                        for key, value in attrs])
                    tag = "<%s%s />" % (tag, strattrs)
                    attributes['tag'] = tag
                    self.handle_uncaptioned_image(attributes)
                    return True

        # Add the tag to the result
        strattrs = "".join([' %s="%s"'
                               % (key, escape(value, quote=True))
                                    for key, value in attrs])
        if tag in self.singleton_tags:
            self.append_data("<%s%s />" % (tag, strattrs))
        else:
            self.append_data("<%s%s>" % (tag, strattrs))

    def handle_uncaptioned_image(self, attributes):
        klass = attributes.get('class', None)
        url = attributes.get('src', None)
        tag = attributes.get('tag', None)
        options = {
            'class': klass,
            'originalwidth': None,
            'originalalt': None,
            'url_path': url,
            'caption': '',
            'image': None,
            'fullimage': None,
            'tag': tag,
            'isfullsize': True,
            'width': attributes.get('width', None),
            }
        options['isfullsize'] = True
        captioned_html = self.captioned_image_template(**options)
        if isinstance(captioned_html, unicode):
            captioned_html = captioned_html.encode('utf8')
        self.append_data(captioned_html)
