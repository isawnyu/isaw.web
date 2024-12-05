import argparse
import csv
import logging
import sys
import transaction
from lxml import html

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy
from Products.CMFCore.utils import getToolByName
from Testing.makerequest import makerequest
from ZODB.POSException import POSKeyError
from zope.component.hooks import setSite
from zope.i18n import Message, translate
from zope.schema.interfaces import ICollection, ITextLine, IURI

logger = logging.getLogger(__name__)
html_parser = html.HTMLParser(remove_blank_text=True)


def safe_encode(value):
    if isinstance(value, Message):
        value = translate(value)
    if isinstance(value, unicode):
        return value.encode('utf-8')
    return value


def spoofRequest(app):
    _policy = PermissiveSecurityPolicy()
    setSecurityPolicy(_policy)
    user = app.acl_users.getUser('admin')
    newSecurityManager(None, user.__of__(app.acl_users))
    return makerequest(app)


def getSite(app, args):
    site_name = args.site
    site = app.unrestrictedTraverse(site_name)
    site.setupCurrentSkin(app.REQUEST)
    setSite(site)
    return site


def ignorable_url(url):
    return (url.startswith('/') or url.startswith('.') or
            url.startswith("http://nohost") or ':' not in url)


def getStringUrl(value):
    # Some AT fields with type 'string' do not contain strings
    if not value or not isinstance(value, basestring):
        return None
    if not(ignorable_url(value)):
        return safe_encode(value)


def getHTMLLinks(html_text):
    """
    Extracts all links from a HTML string
    """
    tree = html.fragment_fromstring(
        html_text, create_parent=True, parser=html_parser
    )
    urls = []
    for el in tree.findall('.//a'):
        url = safe_encode(el.get('href'))
        if url and not ignorable_url(url):
            link_text = safe_encode(''.join(el.itertext()))
            urls.append((url, link_text))
    return urls


def atFieldTitle(field):
    return safe_encode(field.widget.label or field.getName())


def isStringField(field):
    return ITextLine.providedBy(field) or IURI.providedBy(field)


def getUrlValues(item):
    if IDexterityContent.providedBy(item):
        for schema in iterSchemata(item):
            for field in schema:
                if isStringField(field):
                    value = getattr(item, field.__name__, '')
                    url = getStringUrl(value)
                    if url:
                        yield (safe_encode(field.title), url, '')
                elif (ICollection.providedBy(field) and
                    isStringField(field.value_type)):
                    value = getattr(item, field.__name__, '')
                    for line in value:
                        url = getStringUrl(line)
                        if url:
                            yield (safe_encode(field.title), url, None)
                elif IRichText.providedBy(field):
                    value = getattr(item, field.__name__, '')
                    if value and value.output:
                        urls = getHTMLLinks(value.output)
                        for url, link_text in urls:
                            yield (safe_encode(field.title), url, link_text)
    else:
        for field in item.Schema().fields():
            if field.type == 'string':
                value = field.get(item)
                if value:
                    url = getStringUrl(value)
                    if url:
                        yield (atFieldTitle(field), url, None)
            elif field.type == 'lines':
                value = field.get(item)
                for line in value:
                    if isinstance(line, basestring):
                        url = getStringUrl(line)
                        if url:
                            yield (atFieldTitle(field), url, None)
            elif field.type == 'text':
                try:
                    value = field.get(item)
                except (SystemError, POSKeyError):
                    logger.exception(
                        "Error generating AT rich "
                        "text output for {}. Using raw.".format(
                            atFieldTitle(field)
                        )
                    )
                    value = field.getRaw(item)
                if value:
                    urls = getHTMLLinks(value)
                    for url, link_text in urls:
                        yield (atFieldTitle(field), url, link_text)


def findContent(site):
    catalog = getToolByName(site, 'portal_catalog')
    for brain in catalog():
        try:
            obj = brain._unrestrictedGetObject()
        except (AttributeError, KeyError):
            logger.exception(
                "Error getting object for brain {}".format(brain.getPath())
            )
            continue
        yield obj


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Dump all urls in site.'
    )
    parser.add_argument(
        '--site',
        help='Path to plone site from root. Defaults to "Plone"',
        default='Plone'
    )
    parser.add_argument(
        'file',
        help='CSV file to output to.',
        default='urls.csv'
    )
    if sys.argv[0].endswith('/interpreter'):
        del sys.argv[0]
        del sys.argv[1]
    args = parser.parse_args()
    count = 0
    app = spoofRequest(app)
    site = getSite(app, args)
    url_count = 0
    item_count = 0
    with open(args.file, 'w') as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=['URI', 'Path', "Field Name", "Link Text"]
        )
        writer.writeheader()
        for item in findContent(site):
            for field, url, link_text in getUrlValues(item):
                writer.writerow({
                    'URI': url,
                    'Path': item.absolute_url(1)[len(args.site):],
                    'Field Name': field,
                    'Link Text': link_text
                })
                url_count += 1
            item_count += 1
            if item_count % 100 == 0:
                item._p_jar.cacheMinimize()
                transaction.abort()
                print("Processed %s items" % item_count)

    transaction.abort()
    print("Found {} urls across {} content items".format(
        url_count, item_count
    ))
