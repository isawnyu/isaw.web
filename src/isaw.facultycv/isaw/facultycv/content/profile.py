"""Definition of the Profile content type"""

import re
from urlparse import urlparse

from plone import api as plone_api
from plone.dexterity.content import Container
from zope.interface import implementer

from isaw.facultycv.interfaces.profile import IProfile


DOMAIN_LINK_MAP = {
    "facebook.com": {
        "title": "Facebook: {user}",
    },
    "academia.edu": {
        "title": "Academia.edu: {user}",
    },
    "doodle.com": {
        "title": "Doodle Calendar: {user}",
    },
    "linkedin.com": {
        "title": "LinkedIn: {user}",
    },
    "orcid.org": {"title": "ORCID: {user}"},
    "github.com": {
        "title": "GitHub: {user}",
        "regexps": [r"^https?://github.com/(?P<id>[^/]+).*$"],
    },
    "hcommons.org": {
        "title": "Humanities Commons: {user}",
        "regexps": [r"^https?://hcommons.org/members/(?P<id>[^/]+).*$"],
    },
    "twitter.com": {
        "title": "Twitter: {user}",
        "regexps": [r"^https?://twitter\.com/(?P<id>[^/]+).*$"],
    },
    "viaf.org": {
        "title": "VIAF: {user}",
        "regexps": [r"^https?://viaf\.org/viaf/(?P<id>[^/]+).*$"],
    },
    "wikipedia.org": {
        "title": "Wikipedia: {user}",
        "regexps": [
            r"^https?://[^/]+\.wikipedia\.org/wiki/User:(?P<id>[^/]+).*$",
            r"^https?://[^/]+\.wikipedia\.org/wiki/(?!User:)(?P<id>[^/]+).*$",
        ],
    },
    "zotero.org": {
        "title": "Zotero: {user}",
        "regexps": [r"^https?://www\.zotero\.org/(?P<id>[^/]+).*$"],
    },
}


@implementer(IProfile)
class Profile(Container):
    """Profile content type"""

    def get_named_location(self):
        """Return the full named location dict from the registry for this profile's NamedLocation identifier, or None."""
        identifier = self.named_location
        if not identifier:
            return None
        record_name = (
            "isaw.facultycv.interfaces.settings.IISAWFacultyCVSettings.named_locations"
        )
        items = plone_api.portal.get_registry_record(record_name) or []
        for loc in items:
            if loc.get("identifier") == identifier:
                # convert lat/lng to floats
                return {
                    "latitude": float(loc["latitude"]),
                    "longitude": float(loc["longitude"]),
                    "identifier": loc["identifier"],
                    "title": loc["title"],
                }

        return None

    def get_profile_links(self):
        links = self.external_links or []
        results = []
        fullname = self.Title()
        for link in links:
            parsed = urlparse(link)
            if parsed.hostname is None:
                continue
            info = {"link": link, "text": link}
            results.append(info)
            user = fullname
            host = ".".join(parsed.hostname.split(".")[-2:])
            domain_info = DOMAIN_LINK_MAP.get(host)
            if not domain_info:
                link_parts = link.split("|")
                if len(link_parts) > 1:
                    info["link"] = link_parts[0]
                    info["text"] = link_parts[1]
                continue
            text = domain_info["title"]
            for pattern in domain_info.get("regexps", ()):
                match = re.match(pattern, link)
                if not match:
                    continue
                groups = match.groups()
                if groups:
                    user = groups[0]
                    break
            info["text"] = text.format(user=user)
        return results

    # backwards-compatible accessors for catalog metadata columns

    @property
    def Phone(self):
        return self.phone
    
    @property
    def Email(self):
        return self.email
    
    @property
    def Titles(self):
        return self.titles
