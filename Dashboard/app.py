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

# import variables from separate data processing file
from data_preparation import afg_se_df, afg_conflict_df, monthly_cas_df

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# define conflict dropdown menu items
available_charts = ['Event severity over time dot plot', 'Monthly fatalities scatter plot']

#selectable socioeconomic parameters
available_indicators = afg_se_df.columns[2:] 

app.layout = html.Div([
    
    html.H2('Afghanistan Overview'),

#################### CONFLICT ELEMENTS ####################
    html.Div([
        
        html.H4('Conflict Analysis'),

        html.Div([
            dcc.Dropdown(
                id='chart-type',
                options=[{'label': i, 'value': i} for i in available_charts],
                value='Event severity over time dot plot'
            ),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '49%', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),
    
    html.Div([
        dcc.Graph(id='selected-chart')
    ], style={'width': '98%', 'display': 'inline-block', 'padding': '0 20'}),    
    
#################### SOCIOECONOMIC ELEMENTS ####################
    html.Div([
        
        html.H4('Socioeconomic Factors'),

        html.Div([
            html.H6('Primary axis variable'),
            dcc.Dropdown(
                id='primary-yaxis',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='GDP per capita (current US$)'
            ),
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.H6('Secondary axis variable'),
            dcc.Dropdown(
                id='secondary-yaxis',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Electoral democracy index (v2x_polyarchy)'
            )
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    dcc.Graph(id='indicator-chart'),
    
    dcc.RangeSlider(id = 'indicator-range',
        min=afg_conflict_df.year.min(),
        max=afg_conflict_df.year.max(),
        step=1,
        value=[2001, 2018],
        marks = {value: str(value) for value in range(afg_conflict_df.year.min(),afg_conflict_df.year.max())}
                    # do we just want to limit it to the conflict years??
    )  
])
    

# conflict charts
@app.callback(
    Output('selected-chart', 'figure'),
    Input('chart-type', 'value'),
    Input('yaxis-type', 'value')
)
def update_conflict_graph(chart_type, yaxis_type):
    # create the bubble plot
    if(chart_type == available_charts[0]):
        fig = px.scatter(monthly_cas_df, x = 'Month', y = 'events', size = 'marker_size',
                        hover_name = 'Month', # formatting becomes weird for the heading!
                        hover_data = {
                            'marker_size': False,
                            'casualties': True #tried to rename this to 
                        })
        
        fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest',
                        transition_duration=500) # transition is quite buggy
        
        fig.update_yaxes(title='Number of recorded events per month',
                         type='linear' if yaxis_type == 'Linear' else 'log')
        
        return fig
    
    else:
        fig = px.scatter(monthly_cas_df, x = 'Month', y = 'casualties')
        
        fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest',
                         transition_duration=500)
        
        fig.update_yaxes(title='Number of recorded casualties per month',
                         type='linear' if yaxis_type == 'Linear' else 'log')
        
        return fig

# socioeconomic charts
@app.callback(
    Output('indicator-chart', 'figure'),
    Input('primary-yaxis', 'value'),
    Input('secondary-yaxis', 'value'),
    Input('indicator-range', 'value')
)
def update_se_graph_variables(primary_yaxis, secondary_yaxis, indicator_range):
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # dataframe limited to the year range
    dff = afg_se_df[(afg_se_df.Year >= indicator_range[0]) & (afg_se_df.Year <= indicator_range[1])]
    
    fig.add_trace(
    go.Scatter(x=dff['Year'], y=dff[primary_yaxis],
           name = primary_yaxis, mode = 'lines'),
           secondary_y=False
    )
    
    fig.update_yaxes(title_text = primary_yaxis, secondary_y = False)

    fig.add_trace(
        go.Scatter(x=dff['Year'], y=dff[secondary_yaxis],
               name = secondary_yaxis, mode = 'lines'),
               secondary_y=True
    )
    
    fig.update_yaxes(title_text = secondary_yaxis, secondary_y = True)
    
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest',
                      legend_x = 0.01, legend_y = 1,
                     transition_duration=500)
    
    return fig

if __name__ == '__main__':
    app.run_server() 

# open your web browser and go to : http://127.0.0.1:8050/
# if you want to see the dashboard in action