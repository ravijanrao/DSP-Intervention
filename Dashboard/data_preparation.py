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

def create_monthly_casualties_df(conflict_df, marker_size_scaling):
    """
    Accepts a conflict dataframe, returns a dataframe with the monthly casualties and number of events
    The marker_size_scaling parameter is used to scale the size of the 'marker_size' column for eventual plotting
    """
    monthly_cas_df = conflict_df
    monthly_cas_df['Month'] = monthly_cas_df['date_start'].astype('datetime64[ns]') # create datetime object
    monthly_cas_df['events'] = 1

    #Groupby month
    monthly_cas_df = monthly_cas_df.groupby([pd.Grouper(key='Month', freq='M')]).agg({'best':'sum', 'events':'sum'}).reset_index()
    monthly_cas_df['marker_size'] = monthly_cas_df['best'] / marker_size_scaling
    monthly_cas_df.rename({'best': 'casualties'}, axis=1, inplace=True)

    return monthly_cas_df

