# -*- coding: utf-8 -*-

from seraing.urban.dataimport.acropole.mappers import *
from imio.urban.dataimport.mapper import SimpleMapper

OBJECTS_NESTING = [
    (
        'LICENCE', [
            ('CONTACT', []),
            ('PARCEL', []),
            ('DEPOSIT EVENT', []),
            ('DECISION EVENT', []),
            ('ACCEPTABLE DECLARATION EVENT', []),
            ('ACCEPTABLE CONDITIONAL DECLARATION EVENT', []),
            ('UNACCEPTABLE DECLARATION EVENT', []),
            ('COLLEGE REPORT EVENT', []),
            ('TRANSMITTED DECISION EVENT', []),
            ('COMPLETE FOLDER EVENT', []),
            ('INCOMPLETE FOLDER EVENT', []),
        ],
    ),
]

FIELDS_MAPPINGS = {
    'LICENCE':
    {
        'factory': [LicenceFactory],

        'mappers': {
            SimpleMapper: (
                {
                    'from': "Reference",
                    'to': 'referenceDGATLP',
                },
                {
                    'from': 'Objet',
                    'to': 'licenceSubject',
                },
                {
                    'from': 'Delai annonce',
                    'to': 'annoncedDelay',
                },
                {
                    'from': 'Remarques',
                    'to': 'description',
                },
            ),

            IdMapper: {
                'from': 'id',
                'to': 'id',
            },

            ReferenceMapper: {
                'from': ('Numero Permis', 'Reference'),
                'to': 'reference',
            },

            PortalTypeMapper: {
                'from': 'Type',
                'to': ('portal_type', 'folderCategory',)
            },

            ReferenceDGO3Mapper: {
                'from': ('PENReference DGO3', 'Type'),
                'to': 'referenceDGATLP'
            },

            WorklocationMapper: {
                'from': ('AdresseTravauxRue', 'AdresseTravauxNumero', 'AdresseTravauxBoite', 'AdresseTravauxVille'),
                'to': 'workLocations',
            },

            ArchitectMapper: {
               'allowed_containers': ['BuildLicence'],
               'from': ('Nom Architecte', 'Prenom Architecte', 'Societe Architecte'),
               'to': ('architects',)
            },

            FolderZoneTableMapper: {
               'from': ('Plan de Secteur 1', 'Plan de Secteur 2'),
               'to': 'folderZone',
            },

            ParcellingUIDMapper: {
                'from': 'Lotissement',
                'to': 'parcellings',
            },

            IsInSubdivisionMapper: {
                'from': 'Lotissement',
                'to': 'isInSubdivision',
            },

            # WorkTypeMapper: {
            #     'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],
            #     'from': 'Code_220+',
            #     'to': 'workType',
            # },

            InquiryStartDateMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],
                'from': 'DateDebEnq',
                'to': 'investigationStart',
            },

            InquiryEndDateMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],
                'from': 'DateFinEnq',
                'to': 'investigationEnd',
            },

            InvestigationReasonsMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],
                'from': ('ParticularitesEnq1', 'ParticularitesEnq2'),
                'to': 'investigationReasons',
            },

            AskOpinionsMapper: {
                'from': (),
                'to': 'solicitOpinionsTo',
            },

            RubricsMapper: {
                'from': 'DENRubrique1',
                'to': 'rubrics'
            },

            #
            # InquiryReclamationNumbersMapper: {
            #     'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],
            #     'from': 'NBRec',
            #     'to': 'investigationWriteReclamationNumber',
            # },
            #
            # InquiryArticlesMapper: {
            #     'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],
            #     'from': 'Enquete',
            #     'to': 'investigationArticles',
            # },
            #
            # ObservationsMapper: {
            #     'from': ('ParticularitesEnq1', 'ParticularitesEnq2'),
            #     'to': 'description',
            # },
            #
            # TechnicalConditionsMapper: {
            #     'from': ('memo_Autorisation', 'memo_Autorisation2'),
            #     'to': 'locationTechnicalConditions',
            # },

           GeometricianMapper: {
               'allowed_containers': ['ParcelOutLicence'],
               'from': ('LOTGeoTitre', 'LOTGeoNom', 'LOTGeoPrenom'),
               'to': ('geometricians',)
           },

            # ParcellingsMapper: {
            #     'table': 'LOTISSEM',
            #     'KEYS': ('Cle_Urba', 'Cle_Lot'),
            #     'mappers': {
            #         SimpleMapper: (
            #             {
            #                 'from': 'Lot',
            #                 'to': 'subdivisionDetails',
            #             },
            #         ),
            #         ParcellingUIDMapper: {
            #             'from': 'Lotis',
            #             'to': 'parcellings',
            #         },
            #
            #         IsInSubdivisionMapper: {
            #             'from': 'Lotis',
            #             'to': 'isInSubdivision',
            #         }
            #     },
            # },
            #
            # PcaMapper: {
            #     'table': 'PPA',
            #     'KEYS': ('Cle_Urba', 'Cle_PPA'),
            #     'mappers': {
            #         SimpleMapper: (
            #             {
            #                 'from': 'PPA_Affectation',
            #                 'to': 'pcaDetails',
            #             },
            #         ),
            #         PcaUIDMapper: {
            #             'from': 'PPA',
            #             'to': 'pca',
            #         },
            #
            #         IsInPcaMapper: {
            #             'from': 'PPA',
            #             'to': 'isInPCA',
            #         }
            #     },
            # },

            # EnvRubricsMapper: {
            #     'allowed_containers': ['EnvClassOne', 'EnvClassTwo', 'EnvClassThree'],
            #     'from': 'LibNat',
            #     'to': 'description',
            # },
            #
            CompletionStateMapper: {
                'from': ('Date Permis', 'Date Refus', 'Date Permis sur recours', 'Date Refus sur recours', 'DURDecision', 'CU2Decision', 'DENDecision'),
                'to': (),  # <- no field to fill, its the workflow state that has to be changed
            },

            ErrorsMapper: {
                'from': (),
                'to': ('description',),  # log all the errors in the description field
            }
        },
    },

    'PARCEL':
    {
        'factory': [ParcelFactory, {'portal_type': 'PortionOut'}],

        'mappers': {
            ParcelDataMapper: {
                'from': ('Parcelle1section', 'Parcelle1numero', 'Parcelle1numerosuite', 'Parcelle2section', 'Parcelle2numero', 'Parcelle2numerosuite', 'AdresseTravauxVille'),
                'to': (),
            },
        },
    },

    'CONTACT':
    {
        'factory': [ContactFactory],

        'mappers': {
            SimpleMapper: (
                {
                    'from': 'NomDemandeur1',
                    'to': 'name1',
                },
                {
                    'from': 'PrenomDemandeur1',
                    'to': 'name2',
                },
                {
                    'from': ('AdresseDemandeur1'),
                    'to': 'street',
                },
{
                    'from': 'CodePostalDemandeur1',
                    'to': 'zipcode',
                },
{
                    'from': 'VilleDemandeur1',
                    'to': 'city',
                },
            ),

            ContactIdMapper: {
                'from': ('NomDemandeur1', 'PrenomDemandeur1', 'id'),
                'to': 'id',
            },
        },
    },

    'DECISION EVENT':
    {
        'factory': [UrbanEventFactory],
        'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'Declaration', 'EnvClassOne', 'EnvClassTwo'],

        'mappers': {
            DecisionEventTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            DecisionEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            DecisionEventDateMapper: {
                'from': ('Date Permis', 'Date Refus', 'Date Permis sur recours', 'Date Refus sur recours', 'DURDecision', 'DURDateDecision', 'DURDateTransmission', 'CU2DateDecision', 'DENDateIrrecevable', 'DENDatePriseActeSansConditions', 'DENDatePriseActeAvecConditions'),
                'to': 'decisionDate',
            },

            DecisionEventDecisionMapper: {
                'from': ('Date Permis', 'Date Refus', 'Date Permis sur recours', 'Date Refus sur recours', 'DURDecision', 'CU2Decision', 'DENDecision'),
                'to': 'decision',
            },

            DecisionEventNotificationDateMapper: {
                'from': ('Date Permis', 'Date Refus', 'Date Permis sur recours', 'Date Refus sur recours', 'DURDecision', 'DURDateDecision', 'DURDateTransmission', 'CU2DateDecision', 'DENDateIrrecevable', 'DENDatePriseActeSansConditions', 'DENDatePriseActeAvecConditions'),
                'to': 'eventDate',
            }
        },
    },

    'DEPOSIT EVENT':
    {
        'factory': [UrbanEventFactory],

        'mappers': {
            DepositEventMapper: {
                'from': (),
                'to': 'eventtype',
            },

            DepositDateMapper: {
                'from': 'Recepisse',
                'to': 'eventDate',
            },

            DepositEventIdMapper: {
                'from': (),
                'to': 'id',
            }
        },
    },

    'COLLEGE REPORT EVENT':
    {
        'factory': [UrbanEventFactory],
        'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],

        'mappers': {
            CollegeReportTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            CollegeReportIdMapper: {
                'from': (),
                'to': 'id',
            },

            CollegeReportEventDateMapper: {
                'from': ('Rapport du College'),
                'to': 'eventDate',
            }
        },
    },

    'TRANSMITTED DECISION EVENT':
    {
        'factory': [UrbanEventFactory],
        'allowed_containers': ['Declaration'],

        'mappers': {
            TransmittedEventMapper: {
                'from': (),
                'to': 'eventtype',
            },

            DateTransmissionMapper: {
                'from': 'DURDateTransmission',
                'to': 'eventDate',
            },

            DateTransmissionEventIdMapper: {
                'from': (),
                'to': 'id',
            }
        },
    },

    'ACCEPTABLE DECLARATION EVENT':
        {
            'factory': [UrbanEventFactory],
            'allowed_containers': ['EnvClassThree'],

            'mappers': {
                EnvClassThreeAcceptabilityEventMapper: {
                    'from': (),
                    'to': 'eventtype',
                },

                EnvClassThreeAcceptabilityEventIdMapper: {
                    'from': (),
                    'to': 'id',
                },

                EventDateEnvClassThreeAcceptabilityMapper: {
                    'from': ('DENDecision', 'DENDatePriseActeSansConditions',),
                    'to': ('eventDate'),
                },

            },
        },

    'UNACCEPTABLE DECLARATION EVENT':
        {
            'factory': [UrbanEventFactory],
            'allowed_containers': ['EnvClassThree'],

            'mappers': {
                EnvClassThreeUnacceptabilityEventMapper: {
                    'from': (),
                    'to': 'eventtype',
                },

                EnvClassThreeUnacceptabilityEventIdMapper: {
                    'from': (),
                    'to': 'id',
                },

                EventDateEnvClassThreeUnacceptabilityMapper: {
                    'from': ('DENDecision', 'DENDateIrrecevable',),
                    'to': ('eventDate'),
                },

            },
        },


    'ACCEPTABLE CONDITIONAL DECLARATION EVENT':
        {
            'factory': [UrbanEventFactory],
            'allowed_containers': ['EnvClassThree'],

            'mappers': {
                EnvClassThreeCondAcceptabilityEventMapper: {
                    'from': (),
                    'to': 'eventtype',
                },

                EnvClassThreeCondAcceptabilityEventIdMapper: {
                    'from': (),
                    'to': 'id',
                },

                EventDateEnvClassThreeCondAcceptabilityMapper: {
                    'from': ('DENDecision', 'DENDatePriseActeAvecConditions',),
                    'to': ('eventDate'),
                },

            },
        },

    'COMPLETE FOLDER EVENT':
        {
            'factory': [UrbanEventFactory],
            'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'EnvClassOne', 'EnvClassTwo'],

            'mappers': {
                CompleteFolderEventMapper: {
                    'from': (),
                    'to': 'eventtype',
                },

                CompleteFolderEventIdMapper: {
                    'from': (),
                    'to': 'id',
                },

                CompleteFolderDateMapper: {
                    'from': ('PENDtDossierComplet',),
                    'to': ('eventDate'),
                },

            },
        },

    'INCOMPLETE FOLDER EVENT':
        {
            'factory': [UrbanEventFactory],
            'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo', 'EnvClassOne', 'EnvClassTwo'],

            'mappers': {
                IncompleteFolderEventMapper: {
                    'from': (),
                    'to': 'eventtype',
                },

                IncompleteFolderEventIdMapper: {
                    'from': (),
                    'to': 'id',
                },

                IncompleteFolderDateMapper: {
                    'from': ('PENDtDossierIncomplet',),
                    'to': ('eventDate'),
                },

            },
        },
}


OBJECTS_NESTING_OLD = [
    (
        'OLD_LICENCE', [
            ('OLD_CONTACT', []),
            ('OLD_PARCEL', []),
            ('OLD DECISION EVENT', []),
        ],
    ),
]


FIELDS_MAPPINGS_OLD = {
    'OLD_LICENCE':
    {
        'factory': [LicenceFactory],

        'mappers': {
            SimpleMapper: (
                {
                    'from': 'Objet',
                    'to': 'licenceSubject',
                },
            ),

            IdMapper: {
                'from': 'id',
                'to': 'id',
            },

            ReferenceMapper: {
                'from': ('Numero Permis', 'id'),
                'to': 'reference',
            },

            PortalTypeMapper: {
                'from': '',
                'to': ('portal_type', 'folderCategory',)
            },

            WorklocationOldMapper: {
                'from': 'Lieu de construction',
                'to': 'workLocations',
            },

            # ParcellingUIDMapper: {
            #     'from': 'Lotissement',
            #     'to': 'parcellings',
            # },

            IsInSubdivisionMapper: {
                'from': 'Lotissement',
                'to': 'isInSubdivision',
            },

            SubdivisionDetailsMapper: {
                'from': 'Lot',
                'to': 'subdivisionDetails',
            },

            ObservationsOldMapper: {
                'from': 'Remarques',
                'to': 'description',
            },

            CompletionStateMapper: {
                'from': 'Type Decision',
                'to': (),  # <- no field to fill, its the workflow state that has to be changed
            },

            ErrorsMapper: {
                'from': (),
                'to': ('description',),  # log all the errors in the description field
            }
        },
    },

    'OLD_PARCEL':
    {
        'factory': [ParcelFactory, {'portal_type': 'PortionOut'}],

        'mappers': {
            OldParcelDataMapper: {
                'from': 'Cadastre',
                'to': (),
            },
        },
    },

    'OLD_CONTACT':
    {
        'factory': [ContactFactory],

        'mappers': {
            SimpleMapper: (
                {
                    'from': 'Nom Demandeur',
                    'to': 'name1',
                },
                {
                    'from': 'Rue Demandeur',
                    'to': 'street',
                },
            ),

            CityMapper: {
                'from': 'Ville Demandeur',
                'to': 'city',
            },

            PostalCodeMapper: {
                'from': 'Ville Demandeur',
                'to': 'zipcode',
            },

            ContactIdOldMapper: {
                'from': ('Nom Demandeur', 'id'),
                'to': 'id',
            },
        },
    },

    'OLD DECISION EVENT':
    {
        'factory': [UrbanEventFactory],

        'mappers': {
            DecisionEventTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            DecisionEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            OldDecisionEventDateMapper: {
                'from': 'Date Permis',
                'to': 'decisionDate',
            },

            OldDecisionEventDecisionMapper: {
                'from': 'Type Decision',
                'to': 'decision',
            },

            OldDecisionEventNotificationDateMapper: {
                'from': 'Date Permis',
                'to': 'eventDate',
            }
        },
    },
}