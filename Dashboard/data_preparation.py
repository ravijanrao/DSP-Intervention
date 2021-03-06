# Import required libraries
import pickle
import copy
import pathlib
import urllib.request
import math
import datetime as dt
import pandas as pd
import numpy as np
import wbdata as wb

# generate entire dict
def generate_conflict_dict():
    """
    Function to create a complete dict containing all of the data and dataframes for each country
    """

    PATH = pathlib.Path.cwd()
    DATA_PATH = PATH.joinpath("Raw Data")

    countries_list = ['AFG', 'IRQ', 'LKA', 'SOM']

    conflict_dict = {}

    for country in countries_list:

        conflict_dict[country] = {}

        # Conflict df
        country_path_dict = {
            'AFG': 'Conflict_Pickles/12- Afghanistan 2003-2014',
            'IRQ': 'Conflict_Pickles/0- Iraq 2014-',
            'LKA': 'Conflict_Pickles/35- Sri Lanka 1987-1990',
            'SOM': 'Conflict_Pickles/9- Somalia 2007-'
        }
        conflict_df_path = DATA_PATH.joinpath(country_path_dict[country]) # specify the filepath of the conflict df
        conflict_df = pd.read_pickle(conflict_df_path)
        conflict_dict[country]['conflict_df'] = conflict_df

        # Monthly casualties df
        monthly_casualties_df_path = DATA_PATH.joinpath('Monthly_Casualty_Pickles').joinpath(country + '_mc_df')
        monthly_casualties_df = pd.read_pickle(monthly_casualties_df_path)
        conflict_dict[country]['monthly_casualties_df'] = monthly_casualties_df

        # HMI df
        hmi_df_path = DATA_PATH.joinpath('HMI_Pickles').joinpath(country + '_hmi_df')
        hmi_df = pd.read_pickle(hmi_df_path)
        conflict_dict[country]['hmi_df'] = hmi_df

        # Socioeconomic df
        se_df_path = DATA_PATH.joinpath('Socioeconomic_Pickles').joinpath(country + '_se_df')
        se_df = pd.read_pickle(se_df_path)
        conflict_dict[country]['se_df'] = se_df

        # Linkage matrices
        linkage_path = PATH.joinpath(r'Production Data/Linkage_Matrices').joinpath(country) # relevant linkage matrix folder

        setting_dict = {
            '1': '_pure_spatial.npy',
            '2': '_high_spatial_low_temporal.npy',
            '3': '_med_spatial_med_temporal.npy',
            '4': '_low_spatial_high_temporal.npy',
            '5': '_pure_temporal.npy',
        }

        conflict_dict[country]['linkage'] = {}
        for i in range(1,6):
            linkage_matrix_path = linkage_path.joinpath(country + setting_dict[str(i)]) # path to the relevant linkage matrix
            conflict_dict[country]['linkage'][str(i)] = np.load(linkage_matrix_path)

    return conflict_dict

def generate_relevant_entries_dict():
    relevant_entries_dict = { 
        # head of the case description
        'HMIID': 'Short title of the intervention',
        'WBCC': 'World Bank country code of the target country',
        'UCDPID': 'Conflict identification in UCDP datasets',
        'STATUS': 'Status of the intervention',
        'HMISTART': 'Date of the start of the intervention',
        'HMIEND': 'Date of the end of the intervention',
        'ENDTYPE': "Type of the intervention's ending",
        
        # the violent emergency in the target country
        'VIOSTART': 'Date of the beginning of the violent emergency',
        'VIOEND': 'Date of the ending of the violent emergency',
        'ISSUE': 'Main conflict issue of the pre-existing violent emergency acording to UCDP',
        'FATALITY': 'Number of fatalities in the target country due to the violent emergency prior to the intervention',
        'AREA': 'Size of the target target country of the intervention',
        
        # the military intervention
        'UNSC': 'Did the United Nations Security Council mandate or approve the intervention?',
        'REGIOORG': 'Did a regional organization approve the military intervention?',
        'GOVTPERM': 'Did the government in power of the target country permit the intervention?',
        'INTERVEN1': 'Who intervened?',
        'INTERVEN2': 'Who else intervened?',
        'INTERVEN3': 'Was there a further intervener?',
        'COLONY': 'Was one of the three most important interveners a former colonial power or mandate power of the target country or are this intervener and the target country successors of a common state?',
        'SAVING': 'Did the interveners declare the objective of saving strangers?',
        'TARGET': 'Against whom or what was the intervention primarily directed?',
        'TATROOP': 'Best estimate of maximum number of combatants at the disposal of the primarily targeted side',
        'ACTIVE': 'Did the intervening forces actively fulfil their mandate or did they remain passive?',
        'FORCE': 'Did the state or organization that deployed the intervention troops authorize the use of force for any activity?',
        'INTERPOS': 'Did the intervening forces engage in a mission of interposition?',
        'STARINTE': 'When did the intervening forces start interposition?',
        'ENDINTE': 'When did the intervening forces end interposition?',
        'DISARM': 'Did the intervening forces engage in demobilizing and disarming local forces?',
        'STARDISA': 'When did the intervening forces start to demobilize and disarm local forces?',
        'ENDDISA': 'When did the intervening forces end demobilizing and disarming local forces?',
        'CIVILIAN': 'Did the intervening forces engage in protecting civilians?',
        'STARCIVI': 'When did the intervening forces start to protect civilians?',
        'ENDCIVI': 'When did the intervening forces end protecting civilians?',
        'HUMANAID': 'Did the intervening forces engage in protecting the delivery of humanitarian aid?',
        'STARHUMA': 'When did the intervening forces start to protect the delivery of humanitarian aid?',
        'ENDHUMA': 'When did the intervening forces end protecting the delivery of humanitarian aid?',
        'NOFLY': 'Did the intervening troops engage in enforcing a no-fly zone?',
        'STARFLY': 'When did the intervening forces start to enforce a no-fly zone?',
        'ENDLY': 'When did the intervening forces end enforcing a no-fly zone?',
        'SAFEAREA': 'Did the intervening troops engage in enforcing a safe area or protection area on the ground?',
        'STARAREA': 'When did the intervening forces start to enforce a safe area or protection area on the ground?',
        'ENDAREA': 'When did the intervening forces end enforcing a safe area or protection area on the ground?',
        'ENFORCE': 'Did the intervening troops engage in enforcing the acceptance or implementation of a ceasefire for the entire conflict or of a peace agreement?',
        'STARENFO': 'When did the intervening forces start to enforce a ceasefire for the entire conflict or a peace agreement?',
        'ENDENFO': 'When did the intervening forces end enforcing a ceasefire for the entire conflict or a peace agreement?',
        'LOST': 'Did the intervening troops engage in helping one conflict party avoid its military defeat?',
        'STARLOST': 'When did the intervening forces start to help one conflict party avoid its military defeat?',
        'ENDLOST': 'When did the intervening forces end helping one conflict party avoid its military defeat?',
        'REGIME': 'Did the intervening troops engage in bringing about a regime change?',
        'STARREGI': 'When did the intervening forces start to bring about a regime change?',
        'ENDREGI': 'When did the intervening forces end bringing about a regime change?',
        'GROUNDFO': 'Were ground forces deployed in the target country?',
        'GROUNDNO': 'In the case of deployed ground forces, what was their maximum size?',
        'GROUNDPO': 'The maximum size of deployed ground forces in relation to the size of the target country’s population',
        'COUNTTRO': 'Did the intervention face a significant military counter-intervener who deployed troops in the target country?',
        'COUNTARM': 'Did the intervention face a military counter-intervener who delivered arms to the target country?',
        
        # Moves and motives that counteract the intention of saving strangers
        'CONTRA4': 'Did the intervener stress that the people to be saved belong to their people or nation?',
        'CONTRA5': 'Did the intervener declare the intention to prevent a rival from assuming control over the target country?',
        
        # The intervention's aftermath
        'LOSSES': 'Best estimate of number of intervening troops who died during the intervention',
        'LOSSRATE': 'Losses in relation to the number of deployed ground forces',
        'NEWVIOL': 'Did a violent emergency occur in the target country within five years after the end of the intervention?',
        'NEWFATAL': 'Number of fatalities due to the new violent emergency',
        'DISLOCATE': 'Are there indications that the intervention triggered violent emergencies or significantly exacerbated violent emergencies in neighboring countries? ',
        
        # Dict providing interpretation of numerical values of certain outputs
        'Translation': {
                'STATUS':{
                    0:'Without doubt, the intervention does not fulfill the criteria of a humanitarian military intervention, as there was no violent emergency or no use of force or no threat to use force or no declared intention of saving strangers or the declared intention of saving strangers was counteracted.',
                    1:'There are doubts whether counteracting moves or motives were present. Alternatively, the intervention developed out of self-defense but no additional counteracting motives were given. If the violent emergency ends between the authorization of the intervention and troop deployment, it also counts as a borderline case.',
                    2: 'The intervention fulfilled the criteria of a humanitarian military intervention, as there were a violent emergency and a use of force or the threat to use force and  the declared intention of saving strangers and the declared intention of saving strangers was not counteracted.'
                },
                'ENDTYPE':{
                        0:'the intervention is ongoing at the time of coding',
                        1:'end of violent emergency',
                        2:'replacement by another humanitarian military intervention',
                        3:'end of the humanitarian military intervention without a replacement by another while the emergency continued'
                },
                'ISSUE': {
                    1:'terrritory',
                    2:'government',
                    3:'territory and government'
                },
                'NEWVIOL': {
                    0:'the original emergency was ended and no new one occurred',
                    1:'a new violent emergency occurred or the original emergency recurred',
                    -88:'the item is not relevant, as the original emergency or the intervention was still ongoing or less than five years have passed after the intervention'
  }

        }
    }
    return relevant_entries_dict

def generate_se_indicators_dict():
    all_indicator_options = {
    'Demography': ['Population, total', 'Birth rate, crude (per 1,000 people)', 'Death rate, crude (per 1,000 people)',
                   'Population density (people per sq. km of land area)'],
    
    'Economy': ['GDP per capita (current US$)', 'GNI per capita, Atlas method (current US$)',
'Exports of goods and services (% of GDP)','Military expenditure (% of GDP)',
'Consumer price index (2010 = 100)','Food production index (2004-2006 = 100)','Current health expenditure (% of GDP)',
'GDP growth (annual %)','Military expenditure (% of general government expenditure)',
                'Unemployment, youth total (% of total labor force ages 15-24) (modeled ILO estimate)',
'Current education expenditure, total (% of total expenditure in public institutions)',
'Unemployment, total (% of total labor force) (modeled ILO estimate)',
'Children in employment, total (% of children ages 7-14)',
'Armed forces personnel (% of total labor force)'],
    
    'Society': ['People using safely managed drinking water services (% of population)',
'School enrollment, primary (% gross)',
'Life expectancy at birth, total (years)','People using at least basic sanitation services (% of population)',
'Women Business and the Law Index Score (scale 1-100)','Access to electricity (% of population)',
'Multidimensional poverty headcount ratio (% of total population)',
'Proportion of women subjected to physical and/or sexual violence in the last 12 months (% of women age 15-49)',
'Proportion of people living below 50 percent of median income (%)',
'Internally displaced persons, total displaced by conflict and violence (number of people)',
'Strength of legal rights index (0=weak to 12=strong)',
'Adequacy of social protection and labor programs (% of total welfare of beneficiary households)',
'Presence of peace keepers (number of troops, police, and military observers in mandate)',
'Adequacy of social safety net programs (% of total welfare of beneficiary households)']
}

    return all_indicator_options

# define all of the methods used to create the pickles?
# Do we also define the methods used to generate the conflict pickles from UCDP GED? Since we can't upload GED to github due to github 100mb filesize limit
# Is this necessary?

PATH = pathlib.Path.cwd().parent
DATA_PATH = PATH.joinpath("Raw Data")

def create_monthly_casualties_df(conflict_df, marker_size_scaling):
    """
    Accepts a conflict dataframe (generated from the UCDP database), returns a dataframe with the monthly casualties and number of events
    The marker_size_scaling parameter is used to scale the size of the 'marker_size' column for eventual plotting
    Values used were [10.1, 3.7, 7.9, 6.3] respectively for ['AFG', 'IRQ', 'LKA, 'SOM]
    """
    monthly_cas_df = conflict_df
    monthly_cas_df['Month'] = monthly_cas_df['date_start'].astype('datetime64[ns]') # create datetime object
    monthly_cas_df['events'] = 1

    #Groupby month
    monthly_cas_df = monthly_cas_df.groupby([pd.Grouper(key='Month', freq='M')]).agg({'best':'sum', 'events':'sum'}).reset_index()
    monthly_cas_df['marker_size'] = monthly_cas_df['best'] / marker_size_scaling
    monthly_cas_df.rename({'best': 'casualties'}, axis=1, inplace=True)

    return monthly_cas_df


def create_hmi_df(country_code):
    """
    Generates a single-row dataframe describing the characteristics of a HMI as described by the 
    PRIF HMI database. Accepts a WBCC country code ['AFG', 'IRQ', 'SOM', 'LKA'], for example,
    were used to generate the pickles used by the dashboard.
    """

    full_hmi_df_path = DATA_PATH.joinpath('PRIF-dataset-HMI-interventions-v-July-2019.xlsx')
    full_hmi_df = pd.read_excel(full_hmi_df_path) # load the full HMI df
    full_hmi_df.sort_values(by = ['HMISTART'], ascending = False, inplace = True) # sort by recency
    full_hmi_df.index = range(0,41) # reset index

    hmi_df = full_hmi_df[full_hmi_df.WBCC == country_code].iloc[0] # grabs the most recent HMI corresponding to a given WBCC country code
    return hmi_df

def create_se_df(country_code):
    """
    Function used to generate the socioeconomic data dataframe from an excel sheet containing collected socioeconomic
    data from the World Bank for the four countries analysed.
    Takes WBCC country code as input, ['AFG', 'IRQ', 'SOM', 'LKA'] are the available options for which data has been 
    collected.
    """
    full_se_data_path = DATA_PATH.joinpath("AFG_IRQ_LKA_SOM_dataset.xlsx") #path to the full socioeconomic data excel sheet
    full_se_df = pd.read_excel(full_se_data_path)
    se_df = full_se_df[full_se_df.Country == country_code]
    return se_df