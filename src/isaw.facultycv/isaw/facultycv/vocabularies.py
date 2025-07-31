# -*- coding: utf-8 -*-
from plone import api as plone_api
from Products.CMFCore.utils import getToolByName
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


@provider(IVocabularyFactory)
def UsersVocabularyFactory(context):
    acl_users = getToolByName(context, 'acl_users')
    terms = [(SimpleVocabulary.createTerm('', '', 'None'))]

    for user in acl_users.getUsers():
        if user is not None:
            member_id = user.getId()
            member_name = user.getProperty('fullname') or user.getId()
            terms.append(SimpleVocabulary.createTerm(
                user.getId(),
                str(member_id),
                member_name)
            )

    return SimpleVocabulary(terms)


@provider(IVocabularyFactory)
def NamedLocationsVocabulary(context):
    items = plone_api.portal.get_registry_record("isaw.facultycv.interfaces.settings.IISAWFacultyCVSettings.named_locations") or []
    terms = [SimpleTerm(value='', title=u'— None —')]  # Add null option
    terms += [
        SimpleTerm(value=loc["identifier"], title=loc["title"])
        for loc in items
    ]
    return SimpleVocabulary(terms)
