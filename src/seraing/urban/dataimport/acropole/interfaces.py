# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IUrbanImportSource, IUrbanDataImporter


class IAcropoleImporter(IUrbanDataImporter):
    """ marker interface for Acropole data importer """


class IAcropoleImportSource(IUrbanImportSource):
    """ marker interface for Acropole import source """
