from Products.Five.browser import BrowserView
import json


class PeopleView(BrowserView):
    """Base vew class for the @@people-view"""

    JSON_HEADERS = 'name,html_blurb,latitude,longitude,url'

    @property
    def alumni_vrs_map(self, ):
        request = self.request
        if 'alumni' in request.get('URL0'):
            return 'alumni'
        if 'visiting-research-scholars' in request.get('URL0'):
            return 'vrs'
        return ''

    def people(self, depth=1):
        brains = self._query(depth=depth)
        result = []
        for brain in brains:
            profile = brain.getObject()
            named_location = profile.named_location or {}
            data = {
                'id': profile.getId(),
                'name': profile.Title(),
                'email': profile.Email or '',
                'html_blurb': profile.Titles(),
                'url': profile.absolute_url(),
                'has_image': getattr(profile, 'Image', False),
                'image_url': '{}/@@images/Image/mini'.format(
                    profile.absolute_url()
                ),
                'latitude': named_location.get('latitude'),
                'longitude': named_location.get('longitude'),
            }
            result.append(data)

        return result

    def people_json(self):
        results = self.people(depth=-1)
        if not results:
            return ''

        self.request.response.setHeader("Content-Type", "text/json")
        self.request.response.setHeader(
                        "Content-Disposition", 'attachment; filename="people-listing.json"'
                    )

        people = []
        for record in results:
            row = {}
            if not (record['latitude'] and record['longitude']):
                continue

            for h in self.JSON_HEADERS.split(','):
                row[h] = record.get(h, '')

            people.append(row)

        return json.dumps(people)


class PeopleViewFolder(PeopleView):
    """View class for the @@people-view on Folders"""

    def _query(self, depth=1):
        portal_catalog = self.context.portal_catalog
        query = {}
        query['portal_type'] = 'profile'
        folder_path = '/'.join(self.context.getPhysicalPath())
        query['path'] = {'query': folder_path, 'depth': depth}

        return portal_catalog(**query)


class PeopleViewCollection(PeopleView):
    """View class for the @@people-view on Collections"""

    def _query(self):
        return [
            b for b in self.context.queryCatalog() if b.portal_type == 'profile'
        ]
