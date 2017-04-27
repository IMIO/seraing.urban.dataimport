# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapping import table

VALUES_MAPS = {

    'type_map': {
        'PUR': 'BuildLicence',
        'MPL': 'ParcelOutLicence',  # lotissement modifié
        'PLO': 'ParcelOutLicence',
        'DUR': 'Declaration',
        'CU2': 'UrbanCertificateTwo',
        'DEN': 'EnvClassThree',
        'PE2': 'EnvClassTwo',
        'PX2': 'EnvClassTwo',
        'PE1': 'EnvClassOne',
        'PX1': 'EnvClassOne',
        'PU1': 'BuildLicence',
        'PU2': 'BuildLicence',
    },

    'eventtype_id_map': table({
        'header'             : ['decision_event', 'college_report_event', 'deposit_event', 'complete_folder'],
        'BuildLicence'       : ['delivrance-du-permis-octroi-ou-refus', 'rapport-du-college', 'depot-de-la-demande','accuse-de-reception'],
        'ParcelOutLicence'   : ['delivrance-du-permis-octroi-ou-refus', 'rapport-du-college', 'depot-de-la-demande','accuse-de-reception'],
        'Declaration'        : ['deliberation-college', 'rapport-du-college', 'depot-de-la-demande',''],
        'UrbanCertificateOne': ['octroi-cu1', 'rapport-du-college', 'depot-de-la-demande', ''],
        'UrbanCertificateTwo': ['octroi-cu2', 'rapport-du-college', 'depot-de-la-demande', ''],
        'MiscDemand'         : ['deliberation-college', 'rapport-du-college', 'depot-de-la-demande',''],
        'EnvClassOne'        : ['decision', 'rapport-du-college', 'depot-de-la-demande', 'dossier-complet-recevable'],
        'EnvClassTwo'        : ['decision', 'rapport-du-college', 'depot-de-la-demande', 'dossier-complet-recevable'],
        'EnvClassThree'      : ['acceptation-de-la-demande', 'rapport-du-college', 'depot-de-la-demande',''],
    }),

    'solicitOpinionDictionary': {
               '1' :        "service-technique-provincial", #Avis Service technique provincial
               '2' :        "direction-des-cours-deau", #Avis Dir Cours d'eau
               '3' :        "pi", #Avis Zone de secours
               '4' :        "ores", #Avis ORES
               '5' :        "cibe", #Avis Vivaqua
               '6' :        "agriculture", #Avis Dir Développement rural
               '7' :        "dnf", #Avis Département Nature et Forêts
               '8' :        "forces-armees", #Avis Forces armées
               '9' :        "spw-dgo1", #Avis Dir Routes BW
               '10':        "swde", #Avis SWDE/IECBW
               '11':        "belgacom", #Avis PROXIMUS
               '12':        "infrabel", #Avis TEC
               '13':        "ibw", #Avis IBW
               '14':        "voo", #Avis VOO
               '15':        "bec", #Avis Service technique communal
               '16':        "ccatm", #Avis CCATM
               '17':        "owd", #Avis OWD
            },

    'zoneDictionary': {
           "zone d'habitat à caractère rural"                                      : 'zhcr'                                         ,
           "zone agricole"                                                         : 'za'                                           ,
           "zone agricole d'intérêt paysager"                                      : 'zone-agricole-dinteret-paysager'              ,
           "zone d'activité économique industrielle"                               : 'zaei'                                         ,
           "zone d'activité économique industrielle (Wauthier-Braine)"             : 'zaei'                                         ,
           "zone d'activité économique mixte"                                      : 'zaem'                                         ,
           "zone d'aménagement communal concerté"                                  : 'zone-damenagement-communal-concerte'          ,
           "zone d'aménagement différé"                                            : 'zone-damenagement-differe'                    ,
           "zone d'espaces verts"                                                  : 'zev'                                          ,
           "zone d'espaces verts d'intérêt paysager"                               : 'zone-despaces-verts-dinteret-paysager'        ,
           "zone d'extraction"                                                     : 'ze'                                           ,
           "zone d'extraction sur fond de zone agricole"                           : 'zone-dextraction-sur-fond-de-zone-agricole'   ,
           "zone d'habitat"                                                        : 'zh'                                           ,
           "zone de loisirs"                                                       : 'zl'                                           ,
           "zone de parc"                                                          : 'zp'                                           ,
           "zone de parc d'intérêt paysager"                                       : 'zone-de-parc-dinteret-paysager'               ,
           "zone de services publics et d'équipements communautaires"              : 'zspec'                                        ,
           "zone forestière"                                                       : 'zf'                                           ,
           "zone forestière d'intérêt paysager"                                    : 'zone-forestiere-dinteret-paysager'            ,
           "zone non affectée"                                                     : 'zone-non-affectee'                            ,
    },

    'default_date_decision': '09/09/2099',
}