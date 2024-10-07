from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory


@provider(IVocabularyFactory)
def EventTypesVocabulary(context):
    items = [
        ("General", "General"),
        ("Conference", "Conference"),
        ("Exhibition", "Exhibition"),
        ("Lecture", "Lecture"),
        ("Performance", "Performance"),
        ("Seminar", "Seminar"),
        ("Sponsored", "Sponsored"),
    ]
    terms = [SimpleTerm(value=item[0], token=item[0], title=item[1]) for item in items]
    return SimpleVocabulary(terms)

