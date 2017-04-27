# -*- coding: utf-8 -*-

from imio.urban.dataimport.browser.controlpanel import ImporterControlPanel
from imio.urban.dataimport.browser.import_panel import ImporterSettings
from imio.urban.dataimport.browser.import_panel import ImporterSettingsForm


class SeraingImporterSettingsForm(ImporterSettingsForm):
    """ """

class SeraingImporterSettings(ImporterSettings):
    """ """
    form = SeraingImporterSettingsForm


class SeraingImporterControlPanel(ImporterControlPanel):
    """ """
    import_form = SeraingImporterSettings



