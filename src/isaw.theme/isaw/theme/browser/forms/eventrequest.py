from zope import interface, schema
from z3c.form import form, field, button
from plone.z3cform.layout import wrap_form

class IRequestForm(interface.Interface):

    rf_title = schema.TextLine(title=u"Title of Event",
                            required=True)

    rf_sponsor = schema.TextLine(title=u"Sponsoring Department/Faculty",
                            required=False)

    # Event Date, Time and Location
    rf_esd = schema.Date(title=u"Event Start Date", required=True)
    rf_eed = schema.Date(title=u"Event End Date", required=True)
    rf_start_time = schema.Time(title=u"Start Time", required=False)
    rf_end_time = schema.Time(title=u"End Time", required=False)

    rf_number_of_attendees = schema.TextLine(title=u"Number of Attendees", required=False)
    rf_rooms_used = schema.TextLine(title=u"Rooms Used", required=False)


    # Contact Information
    rf_contact_phone = schema.TextLine(title=u"Contact Phone", required=False)
    rf_contact_fax = schema.TextLine(title=u"Contact Fax", required=False)
    rf_contact_email = schema.TextLine(title=u"Contact Email", required=False)
    rf_contact_street_address = schema.TextLine(title=u"Contact Street Address", required=False)
    rf_contact_city = schema.TextLine(title=u"Contact City", required=False)
    rf_contact_state = schema.TextLine(title=u"Contact State", required=False)
    rf_contact_zip = schema.TextLine(title=u"Contact Zip", required=False)

    # Payment Information
    # this is 1 to 1'd only for the sake of capturing the data we need
    # this is not enabled and should never be activated in this current manner

    # Chartfield
    # Type of Card
    # Card Number
    # Security Code

    # Additional Information
    rf_url_info = schema.URI(title=u"URL with more info", required=False)
    rf_vips_attending = schema.TextLine(title=u"VIPs in attendance", required=False)
    rf_vips_name = schema.TextLine(title=u"Name of VIPs", required=False)
    rf_special_instructions = schema.TextLine(title=u"Special Instructions", required=False)

    # Furniture


class RequestForm(form.Form):
    fields = field.Fields(IRequestForm)
    ignoreContext = True
    label = u"Event Request Form"

    @button.buttonAndHandler(u'Submit')
    def handleApply(self, action):
        data, errors = self.extractData()
        print(data['title'])

RequestView = wrap_form(RequestForm)
