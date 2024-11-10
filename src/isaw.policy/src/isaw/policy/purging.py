from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.cachepurging.paths import TraversablePurgePaths
from plone.namedfile.interfaces import INamedBlobImageField
from zope.component import adapter


IMAGE_SCALE_SIZE = (81, 67)
IMAGE_SCALE_NAME = 'image'

IMAGE_SIZES = {'large'   : (768, 768),
               'preview' : (400, 400),
               'mini'    : (200, 200),
               'thumb'   : (128, 128),
               'tile'    :  (64, 64),
               'icon'    :  (32, 32),
               'listing' :  (16, 16),
               }



@adapter(INamedBlobImageField)
class ImagePurgePaths(TraversablePurgePaths):
    """Cache purger for content image content"""
    image_names = ('image',)

    def _image_scales(self):
        props = getToolByName(self.context,
                              'portal_properties')
        if hasattr(props, 'imaging_properties'):
            # plone4
            props = getattr(props, 'imaging_properties')
            sizes = props.getProperty('allowed_sizes', [])
        else:
            # plone5
            sizes = api.portal.get_registry_record(name='plone.allowed_sizes')

        return [p.split()[0] for p in sizes]

    def getRelativePaths(self):
        paths = []
        base = '/' + self.context.virtual_url_path().rstrip('/')
        for name in self.image_names:
            paths.append('{}/{}'.format(base, name))
            paths.append('{}/@@images/{}'.format(base, name))
            for scale in self._image_scales():
                paths.append('{}/@@images/{}/{}'.format(base, name, scale))
                paths.append('{}/{}_{}'.format(base, name, scale))
        return paths


@adapter(ILeadImage)
class LeadimagePurgePaths(ImagePurgePaths):
    image_names = (IMAGE_SCALE_NAME,)

    def _image_scales(self):
        scales = set(super(LeadimagePurgePaths, self)._image_scales())
        scales.add(IMAGE_SCALE_NAME)
        scales |= set(IMAGE_SIZES.keys())
        return list(scales)
