from Products.CMFCore.utils import getToolByName


def profile_updated(obj, event):
    """When a Profile is updated, check for a user_id value.
       If it's set, find the corresponding Plone member and update their
       ProfileReference property, to maintain a bidirectional mapping
       between members and their Profiles.
    """
    membertool = getToolByName(obj, "portal_membership")
    memberID = getattr(obj.aq_base, "user_id", None)
    if memberID:
        member = membertool.getMemberById(memberID)
        if member is not None:
            member.setMemberProperties({'ProfileReference': obj.UID()})
        return
    # We may have *removed* a user ID, and we don't have access to the value
    # previously set, so we have to look at all the members:
    for member in membertool.listMembers():
        if member.getProperty('ProfileReference') == obj.UID():
            member.setMemberProperties({'ProfileReference': ''})
            break
