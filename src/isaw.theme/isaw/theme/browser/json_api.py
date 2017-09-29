import json
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from Products.Five.browser import BrowserView


class UsersVocabularyView(BrowserView):
    """Simple JSON view to render a list of site users accessible to anyone
    with edit permissions"""

    def __call__(self):
        """Renders JSON of users vocabulary"""
        factory = queryUtility(IVocabularyFactory,
                               name=u'isaw.facultycv.Users')
        users = []
        if not factory:
            return users

        terms = factory(self.context)
        for term in terms:
            if term.value:
                users.append({'id': term.value, 'name': term.title})

        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return json.dumps(users)
