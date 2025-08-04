from Products.Five.browser import BrowserView
import csv
from six import StringIO

class PeopleView(BrowserView):
    """Base vew class for the @@people-view"""

    CSV_HEADERS = 'name,html_blurb,latitude,longitude,url'

    @property
    def alumni_vrs_map(self, ):
        request = self.request
        if 'alumni' in request.get('URL0'):
            return 'alumni'
        if 'visiting-research-scholars' in request.get('URL0'):
            return 'vrs'
        return ''

    def people(self):
        brains = self._query()
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

    def people_csv(self):
        results = self.people()
        if not results:
            return ''

        stream = StringIO()
        writer = csv.DictWriter(stream, self.CSV_HEADERS.split(','), quoting=csv.QUOTE_ALL)
        writer.writeheader()

        self.request.response.setHeader("Content-Type", "text/csv")
        self.request.response.setHeader(
                        "Content-Disposition", 'attachment; filename="people.csv"'
                    )

        for record in results:
            row = {}
            for k in self.CSV_HEADERS.split(','):
                row[k] = record[k]
            if not (row['latitude'] and row['longitude']):
                continue
            writer.writerow(row)

        value =stream.getvalue()
        stream.close()
        return value


class PeopleViewFolder(PeopleView):
    """View class for the @@people-view on Folders"""

    def _query(self):
        return self.context.getFolderContents(
            contentFilter={'portal_type': 'profile'}
        )


class PeopleViewCollection(PeopleView):
    """View class for the @@people-view on Collections"""

    def _query(self):
        return [
            b for b in self.context.queryCatalog() if b.portal_type == 'profile'
        ]
