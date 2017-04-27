# -*- coding: utf-8 -*-
import unicodedata

import datetime

from seraing.urban.dataimport.acropole.settings import AcropoleImporterSettings
from seraing.urban.dataimport.acropole.utils import get_state_from_licences_dates, get_date_from_licences_dates, \
    load_architects, load_geometers, load_notaries, load_parcellings, get_point_and_digits
from imio.urban.dataimport.config import IMPORT_FOLDER_PATH

from imio.urban.dataimport.exceptions import NoObjectToCreateException

from imio.urban.dataimport.factory import BaseFactory
from imio.urban.dataimport.mapper import Mapper, FinalMapper, PostCreationMapper
from imio.urban.dataimport.utils import CadastralReference
from imio.urban.dataimport.utils import cleanAndSplitWord
from imio.urban.dataimport.utils import guess_cadastral_reference
from imio.urban.dataimport.utils import identify_parcel_abbreviations
from imio.urban.dataimport.utils import parse_cadastral_reference

from DateTime import DateTime
from Products.CMFPlone.utils import normalizeString
from Products.CMFPlone.utils import safe_unicode

from plone import api
from plone.i18n.normalizer import idnormalizer

import re

import os

#
# LICENCE
#

# factory


class LicenceFactory(BaseFactory):
    def getCreationPlace(self, factory_args):
        path = '%s/urban/%ss' % (self.site.absolute_url_path(), factory_args['portal_type'].lower())
        return self.site.restrictedTraverse(path)

# mappers


class IdMapper(Mapper):

    def __init__(self, importer, args):
        super(IdMapper, self).__init__(importer, args)
        load_architects()
        load_geometers()
        load_notaries()
        load_parcellings()

    def mapId(self, line):
        return normalizeString(self.getData('id'))


class ReferenceMapper(Mapper):

    def mapReference(self, line):
        if AcropoleImporterSettings.file_type == 'old':
            ref = self.getData('Numero Permis') + " old"
            if ref.strip():
                return ref
            else:
                id = self.getData('id')
                return "NC/%s" % (id)  + " old"
        elif AcropoleImporterSettings.file_type == 'new':
            return self.getData('Reference')  + " new"


class ReferenceDGO3Mapper(Mapper):

    def mapReferencedgatlp(self, line):
        type = self.getData('Type')
        if type and type.startswith("PE1") or type.startswith("PE2"):
            dg03ref = self.getData('PENReference DGO3')
            if dg03ref:
                return dg03ref



class PortalTypeMapper(Mapper):
    def mapPortal_type(self, line):
        if AcropoleImporterSettings.file_type == 'old':
            return 'BuildLicence'
        type = self.getData('Type')
        # if type and type.startswith("PE1"):
        #     return "EnvClassOne"
        # elif type and type.startswith("PE2"):
        #     return "EnvClassTwo"
        # else:
        #     raise NoObjectToCreateException
        if type and len(type) >= 3:
            type_map = self.getValueMapping('type_map')
            base_type = type.strip()[0:3]
            # if base_type in ['PE', 'PEX', 'PUN']:
            #     base_type = type.strip()[0:4]
            portal_type = type_map[base_type]

            return portal_type
        else:
            raise NoObjectToCreateException


    def mapFoldercategory(self, line):
        foldercategory = 'uat'
        return foldercategory


class LicenceSubjectMapper(Mapper):
    def mapLicencesubject(self, line):
        object1 = self.getData('Genre de Travaux')
        object2 = self.getData('Divers')
        return '%s %s' % (object1, object2)


class WorklocationMapper(Mapper):
    def mapWorklocations(self, line):
        num = self.getData('AdresseTravauxNumero')
        noisy_words = set(('d', 'du', 'de', 'des', 'le', 'la', 'les', 'à', ',', 'rues', 'terrain', 'terrains', 'garage', 'magasin', 'entrepôt'))
        raw_street = self.getData('AdresseTravauxRue')
        # remove string in () and []
        raw_street = re.sub("[\(\[].*?[\)\]]", "", raw_street)
        street = cleanAndSplitWord(raw_street)
        street_keywords = [word for word in street if word not in noisy_words and len(word) > 1]
        if len(street_keywords) and street_keywords[-1] == 'or':
            street_keywords = street_keywords[:-1]

        locality = self.getData('AdresseTravauxVille')
        street_keywords.extend(cleanAndSplitWord(locality))

        brains = self.catalog(portal_type='Street', Title=street_keywords)
        if len(brains) == 1:
            return ({'street': brains[0].UID, 'number': num},)
        if street:
            self.logError(self, line, 'Couldnt find street or found too much streets', {
                'address': '%s, %s, %s ' % (num, raw_street, locality),
                'street': street_keywords,
                'search result': len(brains)
            })
        return {}


class WorklocationOldMapper(Mapper):
    def mapWorklocations(self, line):
        noisy_words = set(('d', 'du', 'de', 'des', 'le', 'la', 'les', 'à', ',', 'rues', 'terrain', 'terrains', 'garage', 'magasin', 'entrepôt'))
        raw_street = self.getData('Lieu de construction')
        num = ''.join(ele for ele in raw_street if ele.isdigit())
        # remove string in () and []
        raw_street = re.sub("[\(\[].*?[\)\]]", "", raw_street)
        street = cleanAndSplitWord(raw_street)
        street_keywords = [word for word in street if word not in noisy_words and len(word) > 1]
        if len(street_keywords) and street_keywords[-1] == 'or':
            street_keywords = street_keywords[:-1]

        brains = self.catalog(portal_type='Street', Title=street_keywords)
        if len(brains) == 1:
            return ({'street': brains[0].UID, 'number': num},)
        if street:
            self.logError(self, line, 'Couldnt find street or found too much streets', {
                'address': '%s' % (raw_street),
                'street': street_keywords,
                'search result': len(brains)
            })
        return {}


class CityMapper(Mapper):
    def mapCity(self, line):
        city = self.getData('Ville Demandeur')
        return (''.join(ele for ele in city if not ele.isdigit())).strip()


class PostalCodeMapper(Mapper):
    def mapZipcode(self, line):
        zip = self.getData('Ville Demandeur')
        return (''.join(ele for ele in zip if ele.isdigit())).strip()


class ParcellingUIDMapper(Mapper):

    def mapParcellings(self, line):
        title = self.getData('Lotissement')
        if title:
            title = title.replace("(phase I)","").strip()
            title = title.replace("(partie 1)","").strip()
            title = title.replace("(partie 2)","").strip()
            catalog = api.portal.get_tool('portal_catalog')
            brains = catalog(portal_type='ParcellingTerm', Title=title)
            parcelling_uids = [brain.getObject().UID() for brain in brains]
            if len(parcelling_uids) == 1:
                return parcelling_uids
            if parcelling_uids:
                self.logError(self, line, 'Couldnt find parcelling or found too much parcellings', {
                    'titre': '%s' % title,
                    'search result': len(parcelling_uids)
                })



class IsInSubdivisionMapper(Mapper):

    def mapIsinsubdivision(self, line):
        title = self.getData('Lotissement')
        return bool(title)


class SubdivisionDetailsMapper(Mapper):

    def mapSubdivisiondetails(self, line):
        lot = self.getData('Lot')
        return lot


class WorkTypeMapper(Mapper):
    def mapWorktype(self, line):
        worktype = self.getData('Code_220+')
        return [worktype]


class InquiryStartDateMapper(Mapper):
    def mapInvestigationstart(self, line):
        date = self.getData('DateDebEnq')
        if date:
            date = datetime.datetime.strptime(date, "%d/%m/%Y")
        return date


class InquiryEndDateMapper(Mapper):
    def mapInvestigationend(self, line):
        date = self.getData('DateFinEnq')
        if date:
            date = datetime.datetime.strptime(date, "%d/%m/%Y")
        return date

class InvestigationReasonsMapper(Mapper):
    def mapInvestigationreasons(self, line):
        reasons = '<p>%s</p> <p>%s</p>' % (self.getData('ParticularitesEnq1'), self.getData('ParticularitesEnq2'))
        return reasons

class InquiryReclamationNumbersMapper(Mapper):
    def mapInvestigationwritereclamationnumber(self, line):
        reclamation = self.getData('NBRec')
        return reclamation


class InquiryArticlesMapper(PostCreationMapper):
    def mapInvestigationarticles(self, line, plone_object):
        raw_articles = self.getData('Enquete')

        articles = []

        if raw_articles:
            article_regex = '(\d+ ?, ?\d+)°'
            found_articles = re.findall(article_regex, raw_articles)

            if not found_articles:
                self.logError(self, line, 'No investigation article found.', {'articles': raw_articles})

            for art in found_articles:
                article_id = re.sub(' ?, ?', '-', art)
                if not self.article_exists(article_id, licence=plone_object):
                    self.logError(
                        self, line, 'Article %s does not exist in the config',
                        {'article id': article_id, 'articles': raw_articles}
                    )
                else:
                    articles.append(article_id)

        return articles

    def article_exists(self, article_id, licence):
        return article_id in licence.getLicenceConfig().investigationarticles.objectIds()


class AskOpinionsMapper(Mapper):
    def mapSolicitopinionsto(self, line):
        ask_opinions = []
        for i in range(60, 76):
            j = i - 59
            if line[i] == "VRAI":
                solicitOpinionDictionary = self.getValueMapping('solicitOpinionDictionary')
                opinion = solicitOpinionDictionary[str(j)]
                if opinion:
                    ask_opinions.append(opinion)
        return ask_opinions


class RubricsMapper(Mapper):

    def mapRubrics(self, line):
        rubric_list = []
        # licence = self.importer.current_containers_stack[-1]
        # if licence.portal_type == 'EnvClassThree':
        rubric_raw = self.getData('DENRubrique1')
        if rubric_raw:
            rubric_raw.replace("//", "/")
            rubrics = rubric_raw.split("/")
            if rubrics:
                for rubric in rubrics:
                    point_and_digits = get_point_and_digits(rubric)
                    if point_and_digits and '.' in point_and_digits:
                        catalog = api.portal.get_tool('portal_catalog')
                        rubric_uids = [brain.UID for brain in catalog(portal_type='EnvironmentRubricTerm', id=point_and_digits)]
                        if not rubric_uids:
                                self.logError(self, line, 'No rubric found',
                                              {
                                                  'rubric': point_and_digits,
                                              })
                        else:
                            rubric_list.append(rubric_uids[0])


        return rubric_list



class ObservationsMapper(Mapper):
    def mapDescription(self, line):
        description = '<p>%s</p> <p>%s</p>' % (self.getData('ParticularitesEnq1'),self.getData('ParticularitesEnq2'))
        return description


class ObservationsOldMapper(Mapper):
    def mapDescription(self, line):
        description = '<p>%s</p>' % (self.getData('Remarques'))
        return description


class TechnicalConditionsMapper(Mapper):
    def mapLocationtechnicalconditions(self, line):
        obs_decision1 = '<p>%s</p>' % self.getData('memo_Autorisation')
        obs_decision2 = '<p>%s</p>' % self.getData('memo_Autorisation2')
        return '%s%s' % (obs_decision1, obs_decision2)


class ArchitectMapper(PostCreationMapper):
    def mapArchitects(self, line, plone_object):
        # archi_name = '%s %s %s' % (self.getData('Nom Architecte'), self.getData('Prenom Architecte'), self.getData('Societe Architecte'))
        archi_name = ' %s %s' % ( self.getData('Prenom Architecte'), self.getData('Societe Architecte'))
        fullname = cleanAndSplitWord(archi_name)
        if not fullname:
            return []
        noisy_words = ['monsieur', 'madame', 'architecte', '&', ',', '.', 'or', 'mr', 'mme', '/']
        name_keywords = [word.lower() for word in fullname if word.lower() not in noisy_words]
        architects = self.catalog(portal_type='Architect', Title=name_keywords)
        if len(architects) == 0:
            Utils.createArchitect(archi_name)
            architects = self.catalog(portal_type='Architect', Title=name_keywords)
        if len(architects) == 1:
            return architects[0].getObject()
        self.logError(self, line, 'No architects found or too much architects found',
                      {
                          'raw_name': archi_name,
                          'name': name_keywords,
                          'search_result': len(architects)
                      })
        return []


class FolderZoneTableMapper(Mapper):
    def mapFolderzone(self, line):
        folderZone = []
        sectorMap1 = self.getData('Plan de Secteur 1')
        sectorMap2 = self.getData('Plan de Secteur 2')

        zoneDictionnary = self.getValueMapping('zoneDictionary')

        if sectorMap1 in zoneDictionnary:
            folderZone.append(zoneDictionnary[sectorMap1])

        if sectorMap2 in zoneDictionnary:
            folderZone.append(zoneDictionnary[sectorMap2])

        return folderZone


class GeometricianMapper(PostCreationMapper):
    def mapGeometricians(self, line, plone_object):
        name = self.getData('LOTGeoNom')
        firstname = self.getData('LOTGeoPrenom')
        raw_name = firstname + name
        # name = cleanAndSplitWord(name)
        # firstname = cleanAndSplitWord(firstname)
        names = name + ' ' + firstname
        if raw_name:
            geometrician = self.catalog(portal_type='Geometrician', Title=names)
            if len(geometrician) == 0:
                Utils.createGeometrician(name, firstname)
                geometrician = self.catalog(portal_type='Geometrician', Title=names)
            if len(geometrician) == 1:
                return geometrician[0].getObject()
            self.logError(self, line, 'no geometricians found or too much geometricians found',
                          {
                              'raw_name': raw_name,
                              'name': name,
                              'firstname': firstname,
                              'search_result': len(geometrician)
                          })
        return []


class PcaUIDMapper(Mapper):

    def mapPca(self, line):
        title = self.getData('PPA')
        if title:
            catalog = api.portal.get_tool('portal_catalog')
            pca_id = catalog(portal_type='PcaTerm', Title=title)[0].id
            return pca_id
        return []


class IsInPcaMapper(Mapper):

    def mapIsinpca(self, line):
        title = self.getData('PPA')
        return bool(title)


class EnvRubricsMapper(Mapper):

    def mapDescription(self, line):
        rubric = Utils().convertToUnicode(self.getData('LibNat'))
        return rubric


class CompletionStateMapper(PostCreationMapper):
    def map(self, line, plone_object):
        self.line = line
        transition = None
        if AcropoleImporterSettings.file_type == 'old':
            type_decision = self.getData('Type Decision')
            if type_decision == 'REFUS':
                transition = 'refuse'
            else:
                transition = 'accept'
        else:
            if plone_object.portal_type in ['BuildLicence', 'ParcelOutLicence']:
                datePermis = self.getData('Date Permis')
                dateRefus = self.getData('Date Refus')
                datePermisRecours = self.getData('Date Permis sur recours')
                dateRefusRecours = self.getData('Date Refus sur recours')
                transition = get_state_from_licences_dates(datePermis, dateRefus, datePermisRecours, dateRefusRecours)

            elif plone_object.portal_type == 'Declaration':
                if self.getData('DURDecision') == 'Favorable':
                    transition = 'accept'
                elif self.getData('DURDecision') == 'Défavorable':
                    transition = 'refuse'
            elif plone_object.portal_type == 'UrbanCertificateTwo':
                if self.getData('CU2Decision') == 'Favorable':
                    transition = 'accept'
                elif self.getData('CU2Decision') == 'Défavorable':
                    transition = 'refuse'
            elif plone_object.portal_type == 'EnvClassThree':
                if self.getData('DENDecision') == 'irrecevable':
                    transition = 'refuse'
                elif self.getData('DENDecision') == 'OK sans conditions' or self.getData('DENDecision') == 'OK avec conditions':
                    transition = 'accept'

        if transition:
            api.content.transition(plone_object, transition)
            # api.content.transition(plone_object, 'nonapplicable')


class ErrorsMapper(FinalMapper):
    def mapDescription(self, line, plone_object):

        line_number = self.importer.current_line
        errors = self.importer.errors.get(line_number, None)
        description = plone_object.Description()

        error_trace = []
        if errors:
            for error in errors:
                data = error.data
                if 'streets' in error.message:
                    error_trace.append('<p>adresse : %s</p>' % data['address'])
                elif 'notaries' in error.message:
                    error_trace.append('<p>notaire : %s %s %s</p>' % (data['title'], data['firstname'], data['name']))
                elif 'architects' in error.message:
                    error_trace.append('<p>architecte : %s</p>' % data['raw_name'])
                elif 'geometricians' in error.message:
                    error_trace.append('<p>géomètre : %s</p>' % data['raw_name'])
                elif 'parcels' in error.message and AcropoleImporterSettings.file_type == 'old':
                    error_trace.append('<p>parcels : %s </p>' % data['args'])
                elif 'rubric' in error.message.lower():
                    error_trace.append('<p>Rubrique non trouvée : %s</p>' % (data['rubric']))
                elif 'parcelling' in error.message:
                    if data['search result'] == '0':
                        error_trace.append('<p>lotissement non trouvé : %s </p>' % data['titre'])
                    else:
                        error_trace.append("<p>lotissement trouvé plus d'une fois: %s : %s fois</p>" % (data['titre'], data['search result'] ))
                elif 'article' in error.message.lower():
                    error_trace.append('<p>Articles de l\'enquête : %s</p>' % (data['articles']))
        error_trace = ''.join(error_trace)

        return '%s%s' % (error_trace, description)

#
# CONTACT
#

# factory


class ContactFactory(BaseFactory):
    def getPortalType(self, container, **kwargs):
        if container.portal_type in ['UrbanCertificateOne', 'UrbanCertificateTwo', 'NotaryLetter']:
            return 'Proprietary'
        return 'Applicant'

# mappers


class ContactIdMapper(Mapper):
    def mapId(self, line):
        name = '%s%s%s' % (self.getData('NomDemandeur1'), self.getData('PrenomDemandeur1'), self.getData('id'))
        name = name.replace(' ', '').replace('-', '')
        return normalizeString(self.site.portal_urban.generateUniqueId(name))


class ContactIdOldMapper(Mapper):
    def mapId(self, line):
        name = '%s%s' % (self.getData('Nom Demandeur'), self.getData('id'))
        name = name.replace(' ', '').replace('-', '')
        return normalizeString(self.site.portal_urban.generateUniqueId(name))


class ContactTitleMapper(Mapper):
    def mapPersontitle(self, line):
        title1 = self.getData('Civi').lower()
        title = title1 or self.getData('Civi2').lower()
        title_mapping = self.getValueMapping('titre_map')
        return title_mapping.get(title, 'notitle')


class ContactNameMapper(Mapper):
    def mapName1(self, line):
        title = self.getData('Civi2')
        name = self.getData('D_Nom')
        regular_titles = [
            'M.',
            'M et Mlle',
            'M et Mme',
            'M. et Mme',
            'M. l\'Architecte',
            'M. le président',
            'Madame',
            'Madame Vve',
            'Mademoiselle',
            'Maître',
            'Mlle et Monsieur',
            'Mesdames',
            'Mesdemoiselles',
            'Messieurs',
            'Mlle',
            'MM',
            'Mme',
            'Mme et M',
            'Monsieur',
            'Monsieur,',
            'Monsieur et Madame',
            'Monsieur l\'Architecte',
        ]
        if title not in regular_titles:
            name = '%s %s' % (title, name)
        return name


class ContactSreetMapper(Mapper):
    def mapStreet(self, line):
        regex = '((?:[^\d,]+\s*)+),?'
        raw_street = self.getData('D_Adres')
        match = re.match(regex, raw_street)
        if match:
            street = match.group(1)
        else:
            street = raw_street
        return street


class ContactNumberMapper(Mapper):
    def mapNumber(self, line):
        regex = '(?:[^\d,]+\s*)+,?\s*(.*)'
        raw_street = self.getData('D_Adres')
        number = ''

        match = re.match(regex, raw_street)
        if match:
            number = match.group(1)
        return number


class ContactPhoneMapper(Mapper):
    def mapPhone(self, line):
        raw_phone = self.getData('D_Tel')
        gsm = self.getData('D_GSM')
        phone = ''
        if raw_phone:
            phone = raw_phone
        if gsm:
            phone = phone and '%s %s' % (phone, gsm) or gsm
        return phone



#
# PARCEL
#

#factory


class ParcelFactory(BaseFactory):
    def create(self, parcel, container=None, line=None):
        searchview = self.site.restrictedTraverse('searchparcels')
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
            self.logError(self, line, 'Too much parcels found or not enough parcels found', {'args': parcel_args, 'search result': len(found)})
            parcel_args['isOfficialParcel'] = False

        parcel_args['id'] = parcel.id
        parcel_args['partie'] = parcel.partie

        return super(ParcelFactory, self).create(parcel_args, container=container)

    def objectAlreadyExists(self, parcel, container):
        existing_object = getattr(container, parcel.id, None)
        return existing_object

# mappers


class ParcelDataMapper(Mapper):
    def map(self, line, **kwargs):
        section = self.getData('Parcelle1section', line).upper()
        if len(section) > 0:
            section = section[0]
        remaining_reference = '%s %s' % (self.getData('Parcelle1numero', line), self.getData('Parcelle1numerosuite', line))
        if not remaining_reference:
            return []
        abbreviations = identify_parcel_abbreviations(remaining_reference)
        division = '25111' if self.getData('AdresseTravauxVille', line) == 'Wauthier-Braine' else '25015'
        if not remaining_reference or not section or not abbreviations:
            return []
        base_reference = parse_cadastral_reference(division + section + abbreviations[0])

        base_reference = CadastralReference(*base_reference)

        parcels = [base_reference]
        for abbreviation in abbreviations[1:]:
            new_parcel = guess_cadastral_reference(base_reference, abbreviation)
            parcels.append(new_parcel)


        section2 = self.getData('Parcelle2section', line).upper()
        if section2 :
            section2 = section2[0]
            remaining_reference2 = '%s %s' % (self.getData('Parcelle2numero', line), self.getData('Parcelle2numerosuite', line))
            if not remaining_reference2:
                return []

            abbreviations2 = identify_parcel_abbreviations(remaining_reference2)
            if not remaining_reference2 or not section2:
                return []
            base_reference2 = parse_cadastral_reference(division + section2 + abbreviations2[0])

            base_reference2 = CadastralReference(*base_reference2)

            for abbreviation2 in abbreviations2[1:]:
                new_parcel2 = guess_cadastral_reference(base_reference2, abbreviation2)
                parcels.append(new_parcel2)

        return parcels


class OldParcelDataMapper(Mapper):
    def map(self, line, **kwargs):
        raw_parcel = self.getData('Cadastre', line)
        if raw_parcel:
            self.logError(self, line, 'parcels', {'args': raw_parcel})
            # section = raw_parcel[0].upper()
            # remaining_reference = raw_parcel[1:]
            # remaining_reference = remaining_reference.replace("-","").strip()
            # if not remaining_reference:
            #     return []
            # abbreviations = identify_parcel_abbreviations(remaining_reference)
            # division = '25015'
            # if not remaining_reference or not section or not abbreviations:
            #     return []
            # base_reference = parse_cadastral_reference(division + section + abbreviations[0])
            #
            # base_reference = CadastralReference(*base_reference)
            #
            # parcels = [base_reference]
            # for abbreviation in abbreviations[1:]:
            #     new_parcel = guess_cadastral_reference(base_reference, abbreviation)
            #     self.logError(self, line, 'parcels', {'args': new_parcel})
            #     parcels.append(new_parcel)
            #
            # return parcels

        raise NoObjectToCreateException


#
# UrbanEvent deposit
#

# factory
class UrbanEventFactory(BaseFactory):
    def getPortalType(self, **kwargs):
        return 'UrbanEvent'

    def create(self, kwargs, container, line):
        if not kwargs['eventtype']:
            return []
        eventtype_uid = kwargs.pop('eventtype')
        urban_event = container.createUrbanEvent(eventtype_uid, **kwargs)
        return urban_event

#mappers


class DepositEventMapper(Mapper):

    def mapEventtype(self, line):

        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['deposit_event']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class DepositDateMapper(Mapper):

    def mapEventdate(self, line):
        date = self.getData('Recepisse')
        if not date:
            raise NoObjectToCreateException
        date = datetime.datetime.strptime(date, "%d/%m/%Y")
        return date

class DepositEventIdMapper(Mapper):
    def mapId(self, line):
        return 'depot-de-la-demande'

# UrbanEvent transmitted decision

class TransmittedIdMapper(Mapper):

    def mapId(self, line):
        return 'transmis-decision'

class TransmittedEventMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'transmis-decision'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()

class DateTransmissionMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('DURDateTransmission')
        if not date:
            raise NoObjectToCreateException
        date = datetime.datetime.strptime(date, "%d/%m/%Y")
        return date

class DateTransmissionEventIdMapper(Mapper):
    def mapId(self, line):
        return 'transmis-decision'


#
# UrbanEvent ask opinions
#

# factory


class OpinionMakersFactory(BaseFactory):
    """ """

#mappers


class OpinionMakersTableMapper(Mapper):
    """ """
    def map(self, line, **kwargs):
        lines = self.query_secondary_table(line)
        for secondary_line in lines:
            for mapper in self.mappers:
                return mapper.map(secondary_line, **kwargs)
            break
        return []


class OpinionMakersMapper(Mapper):

    def map(self, line):
        opinionmakers_args = []
        for i in range(1, 11):
            opinionmakers_id = self.getData('Org{}'.format(i), line)
            if not opinionmakers_id:
                return opinionmakers_args
            event_date = self.getData('Cont{}'.format(i), line)
            receipt_date = self.getData('Rec{}'.format(i), line)
            args = {
                'id': opinionmakers_id,
                'eventtype': opinionmakers_id,
                'eventDate': event_date and DateTime(event_date) or None,
                'transmitDate': event_date and DateTime(event_date) or None,
                'receiptDate': receipt_date and DateTime(receipt_date) or None,
                'receivedDocumentReference': self.getData('Ref{}'.format(i), line),
            }
            opinionmakers_args.append(args)
        if not opinionmakers_args:
            raise NoObjectToCreateException
        return opinionmakers_args


class LinkedInquiryMapper(PostCreationMapper):

    def map(self, line, plone_object):
        opinion_event = plone_object
        licence = opinion_event.aq_inner.aq_parent
        inquiry = licence.getInquiries() and licence.getInquiries()[-1] or licence
        opinion_event.setLinkedInquiry(inquiry)


#
# Claimant
#

# factory


class ClaimantFactory(BaseFactory):
    def getPortalType(self, container, **kwargs):
        return 'Claimant'

#mappers

class ClaimantIdMapper(Mapper):
    def mapId(self, line):
        name = '%s%s' % (self.getData('RECNom'), self.getData('RECPrenom'))
        name = name.replace(' ', '').replace('-', '')
        if not name:
            raise NoObjectToCreateException
        return normalizeString(self.site.portal_urban.generateUniqueId(name))


class ClaimantTitleMapper(Mapper):
    def mapPersontitle(self, line):
        title = self.getData('Civi_Rec').lower()
        title_mapping = self.getValueMapping('titre_map')
        return title_mapping.get(title, 'notitle')


class ClaimantSreetMapper(Mapper):
    def mapStreet(self, line):
        regex = '((?:[^\d,]+\s*)+),?'
        raw_street = self.getData('RECAdres')
        match = re.match(regex, raw_street)
        if match:
            street = match.group(1)
        else:
            street = raw_street
        return street


class ClaimantNumberMapper(Mapper):
    def mapNumber(self, line):
        regex = '(?:[^\d,]+\s*)+,?\s*(.*)'
        raw_street = self.getData('RECAdres')
        number = ''

        match = re.match(regex, raw_street)
        if match:
            number = match.group(1)
        return number

#
# UrbanEvent second RW
#

#mappers


class SecondRWEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'transmis-2eme-dossier-rw'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class SecondRWEventDateMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('UR_Datenv2')
        date = date and DateTime(date) or None
        if not date:
            raise NoObjectToCreateException
        return date


class SecondRWDecisionMapper(Mapper):
    def mapExternaldecision(self, line):
        raw_decision = self.getData('UR_Avis')
        decision = self.getValueMapping('externaldecisions_map').get(raw_decision, [])
        return decision


class SecondRWDecisionDateMapper(Mapper):
    def mapDecisiondate(self, line):
        date = self.getData('UR_Datpre')
        date = date and DateTime(date) or None
        return date


class SecondRWReceiptDateMapper(Mapper):
    def mapReceiptdate(self, line):
        date = self.getData('UR_Datret')
        date = date and DateTime(date) or None
        return date

#
# UrbanEvent decision
#

#mappers


class DecisionEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['decision_event']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class DecisionEventIdMapper(Mapper):
    def mapId(self, line):
        return 'decision_event'


class DecisionEventDateMapper(Mapper):
    def mapDecisiondate(self, line):
        licence = self.importer.current_containers_stack[-1]
        if licence.portal_type in ['BuildLicence', 'ParcelOutLicence', 'EnvClassOne', 'EnvClassTwo']:
            datePermis = self.getData('Date Permis')
            dateRefus = self.getData('Date Refus')
            datePermisRecours = self.getData('Date Permis sur recours')
            dateRefusRecours = self.getData('Date Refus sur recours')
            date = get_date_from_licences_dates(datePermis, dateRefus, datePermisRecours, dateRefusRecours)
            if not date:
                self.logError(self, line, 'No decision date found')
                raise NoObjectToCreateException
        elif licence.portal_type == 'Declaration':
            date = self.getData('DURDateDecision')

            if not date:
                date = self.getData('DURDateTransmission')
                if not date:
                    decision = self.getData('DURDecision')
                    if decision:
                        date = self.getValueMapping('default_date_decision')
        elif licence.portal_type == 'UrbanCertificateTwo':
            date = self.getData('CU2DateDecision')

        return datetime.datetime.strptime(date, "%d/%m/%Y")


class DecisionEventDecisionMapper(Mapper):
    def mapDecision(self, line):
        licence = self.importer.current_containers_stack[-1]
        if licence.portal_type in ['BuildLicence', 'ParcelOutLicence', 'EnvClassOne', 'EnvClassTwo']:
            datePermis = self.getData('Date Permis')
            dateRefus = self.getData('Date Refus')
            datePermisRecours = self.getData('Date Permis sur recours')
            dateRefusRecours = self.getData('Date Refus sur recours')
            state = get_state_from_licences_dates(datePermis, dateRefus, datePermisRecours, dateRefusRecours)

            if state == 'accept':
                return u'Favorable'
            elif state == 'refuse':
                return u'Défavorable'

        elif licence.portal_type == 'Declaration':
            return self.getData('DURDecision')
        elif licence.portal_type == 'UrbanCertificateTwo':
            return self.getData('CU2Decision')


class DecisionEventNotificationDateMapper(Mapper):
    def mapEventdate(self, line):
        licence = self.importer.current_containers_stack[-1]
        if licence.portal_type in ['BuildLicence', 'ParcelOutLicence', 'EnvClassOne', 'EnvClassTwo']:
            datePermis = self.getData('Date Permis')
            dateRefus = self.getData('Date Refus')
            datePermisRecours = self.getData('Date Permis sur recours')
            dateRefusRecours = self.getData('Date Refus sur recours')
            eventDate = get_date_from_licences_dates(datePermis, dateRefus, datePermisRecours, dateRefusRecours)
        elif licence.portal_type == 'Declaration':
            eventDate = self.getData('DURDateDecision')
            if not eventDate:
                eventDate = self.getData('DURDateTransmission')
                decision = self.getData('DURDecision')
                if decision and not eventDate:
                    eventDate = self.getValueMapping('default_date_decision')
        elif licence.portal_type == 'UrbanCertificateTwo':
            eventDate = self.getData('CU2DateDecision')

        if eventDate:
            return datetime.datetime.strptime(eventDate, "%d/%m/%Y")
        else:
            raise NoObjectToCreateException


class EnvClassThreeCondAcceptabilityEventIdMapper(Mapper):
    def mapId(self, line):
        return 'acceptation-de-la-demande-cond'


class EnvClassThreeCondAcceptabilityEventMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'acceptation-de-la-demande-cond'
        config = urban_tool.getUrbanConfig(licence)
        if hasattr(config.urbaneventtypes, eventtype_id):
            return getattr(config.urbaneventtypes, eventtype_id).UID()


class EventDateEnvClassThreeCondAcceptabilityMapper(Mapper):
    def mapEventdate(self, line):
        eventDate = self.getData('DENDatePriseActeAvecConditions')
        eventDecision = self.getData('DENDecision')
        if eventDecision == "OK avec conditions":
            if not eventDate:
                eventDate = self.getValueMapping('default_date_decision')
            return datetime.datetime.strptime(eventDate, "%d/%m/%Y")
        else:
            raise NoObjectToCreateException
        return eventDate


class EnvClassThreeAcceptabilityEventIdMapper(Mapper):
    def mapId(self, line):
        return 'acceptation-de-la-demande'


class EnvClassThreeAcceptabilityEventMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'acceptation-de-la-demande'
        config = urban_tool.getUrbanConfig(licence)
        if hasattr(config.urbaneventtypes, eventtype_id):
            return getattr(config.urbaneventtypes, eventtype_id).UID()


class EventDateEnvClassThreeAcceptabilityMapper(Mapper):
    def mapEventdate(self, line):
        eventDate = self.getData('DENDatePriseActeSansConditions')
        eventDecision = self.getData('DENDecision')
        if eventDecision == "OK sans conditions":
            if not eventDate:
                eventDate = self.getValueMapping('default_date_decision')
            return datetime.datetime.strptime(eventDate, "%d/%m/%Y")
        else:
            raise NoObjectToCreateException
        return eventDate


class EnvClassThreeUnacceptabilityEventIdMapper(Mapper):
    def mapId(self, line):
        return 'acceptation-de-la-demande'


class EnvClassThreeUnacceptabilityEventMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'refus-de-la-demande'
        config = urban_tool.getUrbanConfig(licence)
        if hasattr(config.urbaneventtypes, eventtype_id):
            return getattr(config.urbaneventtypes, eventtype_id).UID()


class EventDateEnvClassThreeUnacceptabilityMapper(Mapper):
    def mapEventdate(self, line):
        eventDate = self.getData('DENDateIrrecevable')
        eventDecision = self.getData('DENDecision')
        if eventDecision == "irrecevable":
            if not eventDate:
                eventDate = self.getValueMapping('default_date_decision')
            return datetime.datetime.strptime(eventDate, "%d/%m/%Y")
        else:
            raise NoObjectToCreateException
        return eventDate


class OldDecisionEventDateMapper(Mapper):
    def mapDecisiondate(self, line):
        datePermis = self.getData('DENDatePriseActeAvecConditions')
        try:
            d = datetime.datetime.strptime(datePermis, "%d.%m.%y")
            if d > datetime.datetime.now():
                d = datetime(d.year - 100, d.month, d.day)
            return d
        except ValueError:
            return


class OldDecisionEventDecisionMapper(Mapper):
    def mapDecision(self, line):
        decision = self.getData('Type Decision')

        if decision == 'REFUS':
            return u'Défavorable'
        else:
            return u'Favorable'


class OldDecisionEventNotificationDateMapper(Mapper):
    def mapEventdate(self, line):
        datePermis = self.getData('Date Permis')
        try:
            d = datetime.datetime.strptime(datePermis, "%d.%m.%y")
            if d > datetime.datetime.now():
                d = datetime(d.year - 100, d.month, d.day)
            return d
        except ValueError:
            raise NoObjectToCreateException


class CollegeReportTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['college_report_event']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class CollegeReportIdMapper(Mapper):
    def mapId(self, line):
        return 'college_report_event'


class CollegeReportEventDateMapper(Mapper):
    def mapEventdate(self, line):
        eventDate = self.getData('Rapport du College')
        if eventDate:
            return eventDate
        else:
            raise NoObjectToCreateException


class CompleteFolderEventMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['complete_folder']
        config = urban_tool.getUrbanConfig(licence)
        if hasattr(config.urbaneventtypes, eventtype_id):
            return getattr(config.urbaneventtypes, eventtype_id).UID()

class CompleteFolderDateMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('PENDtDossierComplet')
        if not date:
            raise NoObjectToCreateException

        try:
            d = datetime.datetime.strptime(date, "%d/%m/%Y")
            if d > datetime.datetime.now():
                d = datetime(d.year - 100, d.month, d.day)
            return d
        except ValueError:
            raise NoObjectToCreateException


class CompleteFolderEventIdMapper(Mapper):
    def mapId(self, line):
        return 'complete_folder'


class IncompleteFolderEventMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = ('dossier-incomplet')
        config = urban_tool.getUrbanConfig(licence)
        if hasattr(config.urbaneventtypes, eventtype_id):
            return getattr(config.urbaneventtypes, eventtype_id).UID()


class IncompleteFolderDateMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('PENDtDossierIncomplet')
        if not date:
            raise NoObjectToCreateException
        try:
            d = datetime.datetime.strptime(date, "%d/%m/%Y")
            if d > datetime.datetime.now():
                d = datetime(d.year - 100, d.month, d.day)
            return d
        except ValueError:
            raise NoObjectToCreateException


class IncompleteFolderEventIdMapper(Mapper):
    def mapId(self, line):
        return 'incomplete_folder'


#
# UrbanEvent suspension
#


# factory
class SuspensionEventFactory(UrbanEventFactory):

    def create(self, kwargs, container, line):
        if not kwargs['eventtype']:
            return []
        eventtype_uid = kwargs.pop('eventtype')
        suspension_reason = kwargs.pop('suspensionReason')
        urban_event = container.createUrbanEvent(eventtype_uid, **kwargs)
        urban_event.setSuspensionReason(suspension_reason)
        return urban_event
#
# Documents
#

# factory


class DocumentsFactory(BaseFactory):
    """ """
    def getPortalType(self, container, **kwargs):
        return 'File'


# *** Utils ***

class Utils():
    @staticmethod
    def convertToUnicode(string):

        if isinstance(string, unicode):
            return string

        # convert to unicode if necessary, against iso-8859-1 : iso-8859-15 add € and oe characters
        data = ""
        if string and isinstance(string, str):
            try:
                data = unicodedata.normalize('NFKC', unicode(string, "iso-8859-15"))
            except UnicodeDecodeError:
                import ipdb; ipdb.set_trace() # TODO REMOVE BREAKPOINT
        return data

    @staticmethod
    def createArchitect(name):

        idArchitect = idnormalizer.normalize(name + 'Architect').replace(" ", "")
        containerArchitects = api.content.get(path='/urban/architects')

        if idArchitect not in containerArchitects.objectIds():
            new_id = idArchitect
            new_name1 = name

            if not (new_id in containerArchitects.objectIds()):
                    object_id = containerArchitects.invokeFactory('Architect', id=new_id,
                                                        name1=new_name1)

    @staticmethod
    def createGeometrician(name1, name2):

        idGeometrician = idnormalizer.normalize(name1 + name2 + 'Geometrician').replace(" ", "")
        containerGeometricians = api.content.get(path='/urban/geometricians')

        if idGeometrician not in containerGeometricians.objectIds():
            new_id = idGeometrician
            new_name1 = name1
            new_name2 = name2

            if not (new_id in containerGeometricians.objectIds()):
                    object_id = containerGeometricians.invokeFactory('Geometrician', id=new_id,
                                                        name1=new_name1,
                                                        name2=new_name2)