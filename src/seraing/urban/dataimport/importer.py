# -*- coding: utf-8 -*-

from zope.interface import implements

from imio.urban.dataimport.agorawin.importer import AgorawinDataImporter
from seraing.urban.dataimport.interfaces import ISeraingDataImporter


class SeraingDataImporter(AgorawinDataImporter):
    """ """

    implements(ISeraingDataImporter)
