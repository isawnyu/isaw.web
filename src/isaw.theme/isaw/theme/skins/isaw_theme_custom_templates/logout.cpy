## Controller Python Script "logout"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Logout handler
##parameters=

from Products.CMFCore.utils import getToolByName

request = context.REQUEST

mt = getToolByName(context, 'portal_membership')
mt.logoutUser(request)

from Products.CMFPlone.utils import transaction_note
transaction_note('Logged out')

# After logging out of Plone, redirect to the NYU logout page.
# Elected *not* to store this value in external_logout_url site property,
# as this isn't exactly what that property is intended for.
dev_nyu_logout_url = 'https://shibbolethqa.es.its.nyu.edu/idp/profile/Logout'
request.response.redirect(dev_nyu_logout_url)
return
