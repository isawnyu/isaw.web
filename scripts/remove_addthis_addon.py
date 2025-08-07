from zope.component.hooks import setSite
from plone.browserlayer import utils
import transaction


site = app.unrestrictedTraverse('/isaw')
setSite(site)

# Remove all registry entries
registry = site.portal_registry
to_delete = [k for k in registry.records.keys() if 'addthis' in k.lower()]

if not to_delete:
    print("No AddThis registry records found.")
else:
    for key in to_delete:
        del registry.records[key]
        print("Deleted registry key:", key)

# Remove control panel action
cp = site.portal_controlpanel

actions = list(cp.listActions())
found = False

for index, action in enumerate(actions):
    if action.id == "addthis-settings":
        print("Deleting control panel action:", action.id, "-", action.title)
        cp.deleteActions([index])
        found = True
        break

if not found:
    print("No AddThis-related control panel action found.")

# Remove browser layer
try:
    utils.unregister_layer(
        name="collective.addthis"
    )
    print("Removed collective.addthis browser layer.")
except KeyError:
    print("collective.addthis was not registered.")

transaction.commit()
