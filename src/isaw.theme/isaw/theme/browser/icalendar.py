# -*- coding: utf-8 -*-

from plone.app.event.browser.event_listing import EventListingIcal
from plone.app.event.browser.event_listing import construct_icalendar
from plone.app.event.browser.event_listing import RET_MODE_OBJECTS

PRODID = "-//ISAW//ICalendar Support"




class ICalView(EventListingIcal):


    @property
    def ical(self):
        # Get as objects.
        # Don't include occurrences to avoid having them along with their
        # original events and it's recurrence definition in icalendar exports.
        events = self.events(ret_mode=RET_MODE_OBJECTS, expand=False, batch=False)
        cal = construct_icalendar(self.context, events)
        name = "%s.ics" % self.context.getId()
        contents = cal.to_ical()
        self.request.response.setHeader("Content-Type", "text/calendar")
        self.request.response.setHeader(
        "Content-Disposition", 'attachment; filename="isaw_%s.ics"' % name
    )
        self.request.response.setHeader("Content-Length", len(contents))
        self.request.response.write(contents)
