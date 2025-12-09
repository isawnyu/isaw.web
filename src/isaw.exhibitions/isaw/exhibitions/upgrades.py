# -*- coding: utf-8 -*-
from plone import api
from plone.app.upgrade.utils import loadMigrationProfile
from plone.app.workflow.remap import remap_workflow
from plone.dexterity.interfaces import IDexterityFTI
import logging


logger = logging.getLogger(__name__)

PROFILE_ID = 'isaw.exhibitions:default'

def upgrade_5_to_6(contxext):
    """remove skin layer"""
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'skins')