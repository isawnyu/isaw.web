"""Definition of the Seminar content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from isaw.events.content import general
from isaw.events.interfaces import ISeminar
from isaw.events.config import PROJECTNAME

SeminarSchema = general.GeneralSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

SeminarSchema['title'].storage = atapi.AnnotationStorage()
SeminarSchema['description'].storage = atapi.AnnotationStorage()

#override finalizeATCTSchema
def finalizeATCTSchema(schema, folderish=False, moveDiscussion=True):
    """Finalizes an ATCT type schema to alter some fields
       for the event type. This had to be overrided - cwarner
    """
    schema.moveField('relatedItems', pos='bottom')
    if folderish:
        schema['relatedItems'].widget.visible['edit'] = 'invisible'
    schema.moveField('excludeFromNav', after='allowDiscussion')
    if moveDiscussion:
        schema.moveField('allowDiscussion', after='relatedItems')

    schema.moveField('event_Subtitle', after='title')
    schema.moveField('event_Image', after='event_Subtitle')
    schema.moveField('event_Image_caption', after='event_Image')

    # Categorization
    if schema.has_key('subject'):
        schema.changeSchemataForField('subject', 'tags')
    if schema.has_key('relatedItems'):
        schema.changeSchemataForField('relatedItems', 'tags')
    if schema.has_key('location'):
        schema.changeSchemataForField('location', 'default')
        schema.moveField('location', after='event_Speaker')
    if schema.has_key('language'):
        schema.changeSchemataForField('language', 'default')

    # Dates
    if schema.has_key('effectiveDate'):
        schema.changeSchemataForField('effectiveDate', 'default')
        schema.moveField('effectiveDate', after='event_EndDateTime')
    if schema.has_key('expirationDate'):
        schema.changeSchemataForField('expirationDate', 'default')    
        schema.moveField('expirationDate', after='effectiveDate')
    if schema.has_key('creation_date'):
        schema.changeSchemataForField('creation_date', 'dates')    
    if schema.has_key('modification_date'):
        schema.changeSchemataForField('modification_date', 'dates')    

    # Ownership
    if schema.has_key('creators'):
        schema.changeSchemataForField('creators', 'organizers')
    if schema.has_key('contributors'):
        schema.changeSchemataForField('contributors', 'organizers')
    if schema.has_key('rights'):
        schema.changeSchemataForField('rights', 'organizers')

    # Settings
    if schema.has_key('allowDiscussion'):
        schema.changeSchemataForField('allowDiscussion', 'options')
    if schema.has_key('excludeFromNav'):
        schema.changeSchemataForField('excludeFromNav', 'options')
    if schema.has_key('nextPreviousEnabled'):
        schema.changeSchemataForField('nextPreviousEnabled', 'options')

    schemata.marshall_register(schema)
    return schema

finalizeATCTSchema(
    SeminarSchema,
    folderish=True,
    moveDiscussion=False
)


class Seminar(folder.ATFolder):
    """Seminar Event"""
    implements(ISeminar)

    meta_type = "Seminar"
    schema = SeminarSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Seminar, PROJECTNAME)
