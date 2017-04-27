# -*- coding: utf-8 -*-

import csv
from plone.i18n.normalizer import idnormalizer

from Products.CMFPlone.utils import normalizeString
from plone import api

from imio.urban.dataimport.config import IMPORT_FOLDER_PATH
from imio.urban.dataimport.utils import identify_parcel_abbreviations, parse_cadastral_reference, CadastralReference, \
    guess_cadastral_reference


def get_state_from_licences_dates(date_licence, date_refused, date_licence_recourse, date_refused_recourse):

    if date_refused_recourse:
        return 'refuse'
    elif date_licence_recourse:
        return 'accept'
    elif date_refused:
        return 'refuse'
    elif date_licence:
        return 'accept'


def convertToAscii(unicodeString, mode):

    if not isinstance(unicodeString, unicode) or mode != 'replace' and mode != 'ignore':
        raise ValueError

    # convert to ascii, unknown characters are set to '?'/replace mode, ''/ignore mode
    return unicodeString.encode('ascii', mode)


def safe_unicode(value, encoding='utf-8'):
    """Converts a value to unicode, even it is already a unicode string.

    #     >>> from Products.CMFPlone.utils import safe_unicode
    #
    #     >>> safe_unicode('spam')
    #     u'spam'
    #     >>> safe_unicode(u'spam')
    #     u'spam'
    #     >>> safe_unicode(u'spam'.encode('utf-8'))
    #     u'spam'
    #     >>> safe_unicode('\xc6\xb5')
    #     u'\u01b5'
    #     >>> safe_unicode(u'\xc6\xb5'.encode('iso-8859-1'))
    #     u'\u01b5'
    #     >>> safe_unicode('\xc6\xb5', encoding='ascii')
    #     u'\u01b5'
    #     >>> safe_unicode(1)
    #     1
    #     >>> print safe_unicode(None)
    #     None
    # """
    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        try:
            value = unicode(value, encoding)
        except UnicodeDecodeError:
            value = value.decode('utf-8', 'replace')
    return value


def get_date_from_licences_dates(date_licence, date_refused, date_licence_recourse, date_refused_recourse):

    if date_refused_recourse:
        return date_refused_recourse
    elif date_licence_recourse:
        return date_licence_recourse
    elif date_refused:
        return date_refused
    elif date_licence:
        return date_licence


def load_architects():

    csv_filename = 'blc_architects.csv'
    csv_filepath = '{}/{}'.format(IMPORT_FOLDER_PATH, csv_filename)
    csv_file = open(csv_filepath)
    lines = csv.reader(csv_file)

    header_indexes = dict([(headercell.strip(), index) for index, headercell in enumerate(lines.next())])
    cpt = 1
    for architect in lines:
        print "PROCESSING ARCHITECT %i" % cpt
        cpt += 1
        id_architect = idnormalizer.normalize(('architect_%s%s' % (architect[header_indexes['Nom']], architect[header_indexes['Prenom']])).replace(" ", ""))
        containerArchitects = api.content.get(path='/urban/architects')

        if id_architect not in containerArchitects.objectIds():

            if not (id_architect in containerArchitects.objectIds()):
                object_id = containerArchitects.invokeFactory('Architect', id=id_architect,
                                                    name1=architect[header_indexes['Nom']],
                                                    name2=architect[header_indexes['Prenom']],
                                                    phone=architect[header_indexes['Telephone']],
                                                    gsm=architect[header_indexes['Gsm']],
                                                    email=architect[header_indexes['Email']],
                                                    street=architect[header_indexes['Rue et Numero']],
                                                    zipcode=architect[header_indexes['Code postal']],
                                                    city=architect[header_indexes['Localite']])


def load_geometers():

    csv_filename = 'blc_geometres.csv'
    csv_filepath = '{}/{}'.format(IMPORT_FOLDER_PATH, csv_filename)
    csv_file = open(csv_filepath)
    lines = csv.reader(csv_file)

    header_indexes = dict([(headercell.strip(), index) for index, headercell in enumerate(lines.next())])
    cpt = 1
    for geometer in lines:
        print "PROCESSING GEOMETER %i" % cpt
        cpt += 1
        id_geometer = idnormalizer.normalize(('geometer_%s%s' % (geometer[header_indexes['Nom']], geometer[header_indexes['Prenom']])).replace(" ", ""))
        containerGeometers = api.content.get(path='/urban/geometricians')

        if id_geometer not in containerGeometers.objectIds():

            if not (id_geometer in containerGeometers.objectIds()):
                object_id = containerGeometers.invokeFactory('Geometrician', id=id_geometer,
                                                    name1=geometer[header_indexes['Nom']],
                                                    name2=geometer[header_indexes['Prenom']],
                                                    phone=geometer[header_indexes['Telephone']],
                                                    gsm=geometer[header_indexes['Gsm']],
                                                    email=geometer[header_indexes['Email']],
                                                    street=geometer[header_indexes['Rue et Numero']],
                                                    zipcode=geometer[header_indexes['Code postal']],
                                                    city=geometer[header_indexes['Localite']])


def load_notaries():

    csv_filename = 'blc_notaires.csv'
    csv_filepath = '{}/{}'.format(IMPORT_FOLDER_PATH, csv_filename)
    csv_file = open(csv_filepath)
    lines = csv.reader(csv_file)

    header_indexes = dict([(headercell.strip(), index) for index, headercell in enumerate(lines.next())])
    cpt = 1
    for notary in lines:
        print "PROCESSING NOTARY %i" % cpt
        cpt += 1
        id_notary = idnormalizer.normalize(('notary_%s%s' % (notary[header_indexes['Nom']], notary[header_indexes['Prenom']])).replace(" ", ""))
        containerNotaries = api.content.get(path='/urban/notaries')

        if id_notary not in containerNotaries.objectIds():

            if not (id_notary in containerNotaries.objectIds()):
                object_id = containerNotaries.invokeFactory('Notary', id=id_notary,
                                                    name1=notary[header_indexes['Nom']],
                                                    name2=notary[header_indexes['Prenom']],
                                                    phone=notary[header_indexes['Telephone']],
                                                    street='%s %s' % (notary[header_indexes['Adresse1']], notary[header_indexes['Adresse2']]),
                                                    zipcode=notary[header_indexes['Code_postal']],
                                                    city=notary[header_indexes['Ville']])


def load_parcellings():

    csv_filename = 'blc_lotissements.csv'
    csv_filepath = '{}/{}'.format(IMPORT_FOLDER_PATH, csv_filename)
    csv_file = open(csv_filepath)
    lines = csv.reader(csv_file)

    header_indexes = dict([(headercell.strip(), index) for index, headercell in enumerate(lines.next())])
    cpt = 1
    for parcelling in lines:
        print "PROCESSING PARCELLING %i" % cpt
        cpt += 1
        id_parcelling = idnormalizer.normalize(('parcelling%s%s' % (parcelling[header_indexes['Nom du lotisseur']], parcelling[header_indexes['ReferenceRW']].replace("-", "").replace(".", ""))).replace(" ", ""))
        containerParcellings = api.content.get(path='/urban/parcellings')

        if id_parcelling not in containerParcellings.objectIds():

            if not (id_parcelling in containerParcellings.objectIds()):

                object_id = containerParcellings.invokeFactory('ParcellingTerm', id=id_parcelling,
                                                    title='%s %s' % (parcelling[header_indexes['ReferenceRW']], parcelling[header_indexes['Nom du lotisseur']]),
                                                    label=parcelling[header_indexes['Libelle']],
                                                    subdividerName=parcelling[header_indexes['Nom du lotisseur']],
                                                    authorizationDate=parcelling[header_indexes['Date autorisation']],
                                                    DGO4Reference=parcelling[header_indexes['ReferenceRW']],
                                                    numberOfParcels=parcelling[header_indexes['Nombre de lots']])

                parcel = create_parcel(object_id,
                                       parcelling[header_indexes['Parcelle1Section']],
                                       parcelling[header_indexes['Parcelle1Numero']],
                                       parcelling[header_indexes['Parcelle1NumeroSuite']],
                                       parcelling[header_indexes['AdresseLocalite']])





def create_parcel(parcelling, section1, num1, num1suite, division):

    division_label = division
    if len(section1) > 0:
        section1 = section1[0].upper()
    remaining_reference = '%s %s' % (num1, num1suite)
    if not remaining_reference:
        return []
    abbreviations = identify_parcel_abbreviations(remaining_reference)
    division = '25111' if division == 'Wauthier-Braine' else '25015'
    if not remaining_reference or not section1:
        return []
    abbrev = '' if len(abbreviations) == 0  else abbreviations[0]
    base_reference = parse_cadastral_reference(division + section1 + abbrev)

    base_reference = CadastralReference(*base_reference)

    parcels = [base_reference]
    for abbreviation in abbreviations[1:]:
        new_parcel = guess_cadastral_reference(base_reference, abbreviation)
        parcels.append(new_parcel)

    # section2 = self.getData('Parcelle2section', line).upper()
    # if section2:
    #     section2 = section2[0]
    #     remaining_reference2 = '%s %s' % (
    #     self.getData('Parcelle2numero', line), self.getData('Parcelle2numerosuite', line))
    #     if not remaining_reference2:
    #         return []
    #
    #     abbreviations2 = identify_parcel_abbreviations(remaining_reference2)
    #     if not remaining_reference2 or not section2:
    #         return []
    #     base_reference2 = parse_cadastral_reference(division + section2 + abbreviations2[0])
    #
    #     base_reference2 = CadastralReference(*base_reference2)
    #
    #     for abbreviation2 in abbreviations2[1:]:
    #         new_parcel2 = guess_cadastral_reference(base_reference2, abbreviation2)
    #         parcels.append(new_parcel2)

    for parcel in parcels:
        searchview = api.portal.get().restrictedTraverse('searchparcels')
        #need to trick the search browser view about the args in its request
        parcel_args = parcel.to_dict()
        parcel_args.pop('partie')

        for k, v in parcel_args.iteritems():
            searchview.context.REQUEST[k] = v
        #check if we can find a parcel in the db cadastre with these infos
        found = searchview.findParcel(**parcel_args)
        if not found:
            found = searchview.findParcel(browseoldparcels=True, **parcel_args)

        if len(found) == 1 and parcel.has_same_attribute_values(found[0]):
            parcel_args['divisionCode'] = parcel_args['division']
            parcel_args['isOfficialParcel'] = True
        else:
            # api.portal.get().logError(api.portal.get(), None, 'Too much parcels found or not enough parcels found', {'args': parcel_args, 'search result': len(found)})
            parcel_args['isOfficialParcel'] = False

        parcel_args['id'] = parcel.id
        parcel_args['partie'] = parcel.partie
        container = api.content.get(path='/urban/parcellings/' + parcelling)

        object_id = container.invokeFactory('PortionOut',
                                                    title=parcel_args['id'],
                                                    id=parcel_args['id'],
                                                    isOfficialParcel=parcel_args['isOfficialParcel'],
                                                    division=division_label,
                                                    section=parcel_args['section'],
                                                    puissance=parcel_args['puissance'],
                                                    exposant=parcel_args['exposant'],
                                                    radical=parcel_args['radical'],
                                                    bis=parcel_args['bis'],
                                                    divisionCode=parcel_args['division'])

        return object_id


def get_point_and_digits(string):

    return ''.join([letter for letter in string if (letter.isdigit() or letter == '.')]).strip()