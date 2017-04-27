# -*- coding: utf-8 -*-
from imio.urban.dataimport.acropole.importer import AcropoleDataImporter
from seraing.urban.dataimport.acropole import objectsmapping
from seraing.urban.dataimport.acropole import valuesmapping

from zope.interface import implements


from imio.urban.dataimport.mapping import ObjectsMapping, ValuesMapping
from seraing.urban.dataimport.acropole.interfaces import IAcropoleImporter


class SeraingAcropoleMapping(ObjectsMapping):
    """ """

    def getObjectsNesting(self):
        return objectsmapping.OBJECTS_NESTING

    def getFieldsMapping(self):
        return objectsmapping.FIELDS_MAPPINGS


class SeraingAcropoleValuesMapping(ValuesMapping):
    """ """

    def getValueMapping(self, mapping_name):

        return valuesmapping.VALUES_MAPS.get(mapping_name, None)


class LicencesImporter(AcropoleDataImporter):
    """ """

    implements(IAcropoleImporter)

    def __init__(self, db_name='chatelet_20160829', table_name='wrkdossier', key_column='WRKDOSSIER_ID', savepoint_length=0):
        super(AcropoleDataImporter, self).__init__(db_name, table_name, key_column, savepoint_length)

