# Import required libraries
import pickle
import copy
import pathlib
import urllib.request
import dash
from jupyter_dash import JupyterDash
import math
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go 
from plotly.subplots import make_subplots

# get relative data folder
PATH = pathlib.Path.cwd().parent
DATA_PATH = PATH.joinpath("Raw Data")

### prepare afghanistan socioeconomic data ###
raw_se_data_path = DATA_PATH.joinpath("AFG_IRQ_LKA_SOM_dataset.xlsx")
raw_se_df = pd.read_excel(raw_se_data_path)
afg_se_df = raw_se_df[raw_se_df.Country == 'AFG']

### prepare afghanistan conflict data ###
afg_conflict_path = DATA_PATH.joinpath('Conflict_Pickles/12- Afghanistan 2003-2014')
afg_conflict_df = pd.read_pickle(afg_conflict_path)

# monthly fatalities, best guess, marker size
monthly_cas_df = afg_conflict_df.copy()
monthly_cas_df['Month'] = monthly_cas_df['date_start'].astype('datetime64[ns]') # create datetime object
monthly_cas_df['events'] = 1
#Groupby month
monthly_cas_df = monthly_cas_df.groupby([pd.Grouper(key='Month', freq='M')]).agg({'best':'sum', 'events':'sum'}).reset_index()
monthly_cas_df['marker_size'] = monthly_cas_df['best'] / 10
monthly_cas_df.rename({'best': 'casualties'}, axis=1, inplace=True)



# Return all data pertaining to a country function:
# needs to be extended for thijs' analysis! Also with the data from allard/naomi? i.e. neighbours
country_code_dict = {
    'Afghanistan': 'AFG',
    'Iraq': 'IRQ',
    'Somalia': 'SOM',
    'Sri Lanka': 'LKA'
}


# define all of the methods used to create the pickles
# Do we also define the methods used to generate the conflict pickles from UCDP GED? Since we can't upload GED to github due to github 100mb filesize limit
# Is this necessary?


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
