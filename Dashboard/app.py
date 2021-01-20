# Import required libraries
import pickle
import copy
import pathlib
import urllib.request

import datetime as dt
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from scipy.cluster.hierarchy import fcluster

# import variables from separate data processing file
from data_preparation import generate_conflict_dict

conflict_dict = generate_conflict_dict()

app = dash.Dash(__name__)

conflict_df = conflict_dict["AFG"]["conflict_df"]

# dict to convert from country name to country code
country_code_dict = {
    "Afghanistan": "AFG",
    "Iraq": "IRQ",
    "Somalia": "SOM",
    "Sri Lanka": "LKA",
}

# define conflict dropdown menu items
available_charts = [
    "Event severity over time dot plot",
    "Monthly fatalities scatter plot",
]

# selectable socioeconomic parameters
# available_indicators = se_df.columns[2:]
available_indicators = conflict_dict["AFG"]["se_df"].columns[2:]

# import the linkage matrix
# linkage_matrix = get_linkage_matrix('Afghanistan', 3)
# linkage_matrix = conflict_dict['AFG']['linkage']['3']

app.layout = html.Div(
    [
        # The sidebar div
        html.Div(
            className="grid-item grid-sidebar",
            style={"grid-area": "side"},
            children=[
                html.H2("[DSP dashboard concept]"), 
                html.Label("Select conflict"),
                dcc.Dropdown(
                    id="selected-country",
                    options=[{"label": i, "value": i} for i in country_code_dict],
                    value="Afghanistan"
                ),
                html.P("Additional text explaning the conflict.")
            ]
        ), 

        html.Div(
            className="grid-item grid-graph-component",
            style={"grid-area": "map"},
            children=[
                dcc.Graph(id="main-map")
            ]
        ),       
        
        # Bubble chart component
        html.Div(
            className="grid-item grid-graph-component",
            style={"grid-area": "country-overview"},
            children=[
                html.H4("Conflict Analysis", className="component__title"),
                html.Div(
                    className="side-by-side-input",
                    children=[
                        dcc.Dropdown(
                            id="chart-type",
                            options=[
                                {"label": i, "value": i} for i in available_charts
                            ],
                            value="Event severity over time dot plot",
                        ),
                        dcc.RadioItems(
                            id="yaxis-type",
                            className="radio-input",
                            options=[
                                {"label": i, "value": i} for i in ["Linear", "Log"]
                            ],
                            value="Linear",
                        )
                    ]
                ),
                dcc.Graph(id="selected-chart")
            ]
        ),

        # 3d-scatter-plot / SpaceTime clustering
        html.Div(
            className="grid-item grid-graph-component",
            style={"grid-area": "3d-scatter"},
            children=[
                html.H4("Space-time clustering"),
                html.Label("Select cluster size"),
                dcc.Slider(
                    id="cluster-size-slider", min=0, max=0.6, step=0.02, value=0.16
                ),
                dcc.Graph(id="3d-scatter-plot"),
            ]
        ),

        #     style={
        #         "borderBottom": "thin lightgrey solid",
        #         "backgroundColor": "rgb(250, 250, 250)",
        #         "padding": "10px 5px",
        #         "width": "49%",
        #     },
        # ),
        #################### SOCIOECONOMIC ELEMENTS ####################

        html.Div(
            className="grid-item grid-graph-component",
            style={"grid-area": "se-factors"},
            children=[
                html.H4("Socioeconomic Factors"),
                html.Div(
                    className="side-by-side-input",
                    children=[
                        html.Div(
                            [
                                html.H6("Primary axis variable"),
                                dcc.Dropdown(
                                    id="primary-yaxis",
                                    options=[
                                        {"label": i, "value": i} for i in available_indicators
                                    ],
                                    value="GDP per capita (current US$)",
                                )
                            ]
                        ),
                        html.Div(
                            [
                                html.H6("Secondary axis variable"),
                                dcc.Dropdown(
                                    id="secondary-yaxis",
                                    options=[
                                        {"label": i, "value": i} for i in available_indicators
                                    ],
                                    value="Electoral democracy index (v2x_polyarchy)",
                                ),
                            ],
                        )
                    ]
                ),
                dcc.Graph(id="indicator-chart"),
                dcc.RangeSlider(
                    id="indicator-range",
                    min=conflict_df.year.min(),
                    max=conflict_df.year.max(),
                    step=1,
                    value=[conflict_df.year.min(), conflict_df.year.max()],
                    marks={
                        value: str(value)
                        for value in range(conflict_df.year.min(), conflict_df.year.max(), 2)
                    }
                ),
                
            ]
        ),

        html.Div(
            className="grid-item grid-graph-component",
            style={"grid-area": "st-knox"},
            children=[
                html.H4("Space-time contingency tables")
            ]
        ),
    ], className="grid-container"
)

#########################################################
#################### Conflict charts ####################
#########################################################

@app.callback(
    Output("main-map", "figure"),
    Input("selected-country", "value")
)
def update_map(selected_country):
    url = 'https://raw.githubusercontent.com/kefeimo/DataScienceBlog/master/2.geo_plot/df_mapbox_demo.csv'
    df_plot_tmp = pd.read_csv(url)
    mapbox_access_token =  'pk.eyJ1IjoidGVzY2hvdXRlbiIsImEiOiJja2s0M2t0cGkxaDdkMnZycnh3MnJmN2ttIn0.ftu0gggzcawisWSA2KV6kw'
    px.set_mapbox_access_token(mapbox_access_token)
    fig = px.scatter_mapbox(df_plot_tmp, lat="latitude", lon="longitude", color="gender", zoom=3,
                           mapbox_style="light")

    fig.update_layout(autosize=False, margin=dict(t=0, b=0, l=0, r=0))
    fig.update_layout(showlegend=False)

    return fig

#### Standard conflict charts ####
@app.callback(
    Output("selected-chart", "figure"),
    Input("selected-country", "value"),
    Input("chart-type", "value"),
    Input("yaxis-type", "value"),
)
def update_conflict_graph(selected_country, chart_type, yaxis_type):
    # create the bubble plot
    country = country_code_dict[selected_country]
    if chart_type == available_charts[0]:
        fig = px.scatter(
            conflict_dict[country]["monthly_casualties_df"],
            x="Month",
            y="events",
            size="marker_size",
            # fig = px.scatter(monthly_casualties_df, x = 'Month', y = 'events', size = 'marker_size',
            hover_name="Month",  # formatting becomes weird for the heading!
            hover_data={
                "marker_size": False,
                "casualties": True,  # tried to rename this to
            },
        )
    else:
        fig = px.scatter(
            conflict_dict[country]["monthly_casualties_df"], x="Month", y="casualties"
        )

    fig.update_layout(
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        hovermode="closest",
        transition_duration=500,
    )  # transition is quite buggy

    fig.update_yaxes(
        title="Number of recorded events per month",
        type="linear" if yaxis_type == "Linear" else "log",
    )

    return fig

#### 3d chart ####
#### NEEDS TO BE UPDATED TO ALLOW FOR CHANGE OF SETTING! #####
@app.callback(
    Output("3d-scatter-plot", "figure"),
    Input("selected-country", "value"),
    Input("cluster-size-slider", "value"),
)
def update_3d_graph(selected_country, cutoff_value):
    country = country_code_dict[selected_country]

     # Drop cols & create date instances
    # all of this data processing is not necessary unless we change country!
    df_clean = conflict_dict[country]['conflict_df'].loc[:,['date_start', 'best', 'latitude', 'longitude', 'side_a', 'side_b']]
    df_clean['date'] = pd.to_datetime(df_clean['date_start'])

    # Calculate days from earliest event for faster comparison
    first_date = df_clean['date'].min()
    df_clean['days_from_earliest'] = (df_clean['date'] - first_date).dt.days

    # Rename cols
    # df_clean = df_clean.rename(columns={"latitude": "lat", "longitude": "lon"})

    # grab relevant linkage matrix
    linkage_matrix = conflict_dict[country]['linkage']['3']
 
    df_clean['cluster'] = fcluster(linkage_matrix, cutoff_value, criterion = 'distance')

    fig = px.scatter_3d(df_clean, 
        x='latitude', y='longitude', z='days_from_earliest',
        color="cluster",
        hover_data = {
            'side_a': True,
            'side_b': True,
            'date': True
        }
    )

    # fig.update_layout(margin={'l': 40, 'b': 40, 't': 0, 'r': 0})
#     fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest',
#     transition_duration=500) # transition is quite buggy

    return fig

######################################################
################ Socioeconomic charts ################
######################################################

@app.callback(
    Output('indicator-chart', 'figure'),
    Input('selected-country', 'value'),
    Input('primary-yaxis', 'value'),
    Input('secondary-yaxis', 'value'),
    Input('indicator-range', 'value')
)
def update_se_graph_variables(selected_country, primary_yaxis, secondary_yaxis, indicator_range):
    
    country = country_code_dict[selected_country]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # dataframe limited to the year range
    se_df = conflict_dict[country]['se_df']
    dff = se_df[(se_df.Year >= indicator_range[0]) & (se_df.Year <= indicator_range[1])]
    
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
    app.run_server(debug=False, port=3007) 

# open your web browser and go to : http://127.0.0.1:8050/
# if you want to see the dashboard in action   # Drop cols
