from DateTime import DateTime
from Products.ATContentTypes.lib.calendarsupport import ICS_HEADER
from Products.ATContentTypes.lib.calendarsupport import ICS_FOOTER
from Products.ATContentTypes.lib.calendarsupport import ICS_EVENT_START
from Products.ATContentTypes.lib.calendarsupport import ICS_EVENT_END
from Products.ATContentTypes.lib.calendarsupport import n2rn
from Products.ATContentTypes.lib.calendarsupport import rfc2445dt
from Products.ATContentTypes.lib.calendarsupport import vformat
from Products.ATContentTypes.lib.calendarsupport import foldLine
from Products.Five import BrowserView
from StringIO import StringIO


PRODID = "-//ISAW//ICalendar Support"


def get_ical(result):
    """get iCal data
    """
    out = StringIO()
    map = {
        'dtstamp': rfc2445dt(DateTime()),
        'created': rfc2445dt(DateTime(result.CreationDate())),
        'uid': result.UID(),
        'modified': rfc2445dt(DateTime(result.ModificationDate())),
        'summary': vformat(result.Title()),
        'startdate': rfc2445dt(DateTime(result.start)),
        'enddate': rfc2445dt(DateTime(result.end)),
        }
    out.write(ICS_EVENT_START % map)

    description = result.Description()
    if description:
        out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))

    subject = result.Subject()
    if subject:
        out.write('CATEGORIES:%s\n' % ', '.join(subject))

    out.write(ICS_EVENT_END)
    return out.getvalue()


class ICalView(BrowserView):

    def __call__(self):
        """iCalendar output
        """
        self.request.response.setHeader('Content-Type', 'text/calendar')
        self.request.response.setHeader('Content-Disposition',
                                        'attachment; filename="isaw_%s.ics"'
                                        % self.context.getId())
        out = StringIO()
        out.write(ICS_HEADER % {'prodid': PRODID})
        results = self.context.listFolderContents(
            contentFilter={"portal_type": "Event"})
        for result in results:
            out.write(get_ical(result))
        out.write(ICS_FOOTER)
        return n2rn(out.getvalue())
