# Import required libraries
import pickle
import copy
import pathlib
import urllib.request
import math
import datetime as dt
import pandas as pd
import numpy as np



# Return all data pertaining to a country function:
# needs to be extended for thijs' analysis! Also with the data from allard/naomi? i.e. neighbours data

def get_country_df(country_name):

    PATH = pathlib.Path.cwd()
    DATA_PATH = PATH.joinpath("Raw Data")

    """
    Return the dataframes used to analyse the country, retrieved from pickles contained in the relevant folders
    Input is a country name, with the choice of ['Afghanistan', 'Iraq', 'Somalia', 'Sri Lanka']
    FOUR different dataframes returned: the conflict df, the monthly casualties_df, the hmi df, and the socioeconomic factor df
    """

    country_code_dict = {
        'Afghanistan': 'AFG',
        'Iraq': 'IRQ',
        'Somalia': 'SOM',
        'Sri Lanka': 'LKA'
    }

    country = country_code_dict[country_name] # select the country code of the input country

    # Grab the full conflict df
    country_path_dict = {
        'AFG': 'Conflict_Pickles/12- Afghanistan 2003-2014',
        'IRQ': 'Conflict_Pickles/0- Iraq 2014-',
        'LKA': 'Conflict_Pickles/35- Sri Lanka 1987-1990',
        'SOM': 'Conflict_Pickles/9- Somalia 2007-'
    }

    conflict_df_path = DATA_PATH.joinpath(country_path_dict[country]) # specify the filepath of the conflict df
    conflict_df = pd.read_pickle(conflict_df_path)

    # Grab the monthly casualties df (could also generate this directly with a function?)
    monthly_casualties_df_path = DATA_PATH.joinpath('Monthly_Casualty_Pickles').joinpath(country + '_mc_df')
    monthly_casualties_df = pd.read_pickle(monthly_casualties_df_path)

    # Grab the HMI df (could also generate this directly with a function?)
    hmi_df_path = DATA_PATH.joinpath('HMI_Pickles').joinpath(country + '_hmi_df')
    hmi_df = pd.read_pickle(hmi_df_path)

    # Grab the socioeconomic factor df (could also generate this directly with a function?)
    se_df_path = DATA_PATH.joinpath('Socioeconomic_Pickles').joinpath(country + '_se_df')
    se_df = pd.read_pickle(se_df_path)

    return conflict_df, monthly_casualties_df, hmi_df, se_df

# Here we grab/generate a linkage matrix every time we change settings
# the other option would be to grab all 5 linkage matrices for the country in the function above
def get_linkage_matrix(country_name, setting):
    """
    Grab the relevant linkage matrix for a country, based on the selected setting (1-5 currently)
    """
    PATH = pathlib.Path.cwd()

    setting_dict = {
        '1': '_pure_spatial.npy',
        '2': '_high_spatial_low_temporal.npy',
        '3': '_med_spatial_med_temporal.npy',
        '4': '_low_spatial_high_temporal.npy',
        '5': '_pure_temporal.npy',
    }

    setting = str(setting)

    country_code_dict = {
        'Afghanistan': 'AFG',
        'Iraq': 'IRQ',
        'Somalia': 'SOM',
        'Sri Lanka': 'LKA'
    }

    country_code = country_code_dict[country_name]
    
    linkage_path = PATH.joinpath('Linkage_Matrices').joinpath(country_code) # relevant linkage matrix folder
    linkage_matrix_path = linkage_path.joinpath(country_code + setting_dict[setting]) # grab the relevant linkage matrix path
    linkage_matrix = np.load(linkage_matrix_path)

    return linkage_matrix


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
        linkage_path = PATH.joinpath('Linkage_Matrices').joinpath(country) # relevant linkage matrix folder

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



# define all of the methods used to create the pickles
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