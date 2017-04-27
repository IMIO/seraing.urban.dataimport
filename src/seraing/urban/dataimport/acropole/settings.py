# -*- coding: utf-8 -*-

from imio.urban.dataimport.acropole.importer import AcropoleDataImporter
from imio.urban.dataimport.acropole.interfaces import IAcropoleDataImporter
from imio.urban.dataimport.browser.adapter import ImporterFromSettingsForm
from imio.urban.dataimport.browser.import_panel import ImporterSettings

from zope.interface import implements

from imio.urban.dataimport.acropole.settings import AcropoleImporterFromImportSettings


class AcropoleImporterSettings(ImporterSettings):
    """
    """
    file_type = None

class SeraingAcropoleImporterFromImportSettings(AcropoleImporterFromImportSettings):
    """ """

    def get_importer_settings(self):
        """
        Return the db name to read.
        """
        AcropoleImporterSettings.file_type = 'new'
        settings = super(SeraingAcropoleImporterFromImportSettings, self).get_importer_settings()
        db_settings = {
            'key_column': 'id',
            'csv_filename': 'BLC-TOUS',
            # 'csv_filename': 'seraing_new_20170223.csv',
        }

        settings.update(db_settings)

        return settings

