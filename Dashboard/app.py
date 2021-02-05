# Import required libraries
import pickle
from math import log
import copy
import pathlib
import urllib.request

import datetime as dt
import numpy as np
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

import wbdata as wb

# import variables from separate data processing file
from data_preparation import generate_conflict_dict, generate_relevant_entries_dict, generate_se_indicators_dict
from sidebar_generator import sidebar_generator

conflict_dict = generate_conflict_dict() #dict containing conflict dataframes
relevant_entries_dict = generate_relevant_entries_dict() #dict of conflict descriptors
all_se_options = generate_se_indicators_dict() # dict of all socioeconomic indicators

# Load knox tables data
with open(r"Production Data/Knox tables/knox_tables_v3.pickle", "rb") as handle:
    knox_data = pickle.load(handle)

mapbox_access_token = "pk.eyJ1IjoidGVzY2hvdXRlbiIsImEiOiJja2s0M2t0cGkxaDdkMnZycnh3MnJmN2ttIn0.ftu0gggzcawisWSA2KV6kw"
px.set_mapbox_access_token(mapbox_access_token)

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

app.layout = html.Div(
    [
        # The sidebar div
        html.Div(
            className="grid-item grid-text-component grid-text-sidebar",
            style={"grid-area": "side"},
            children=[
                html.H2("[UVA x TNO HMI-VAST]"),
                html.Label("Select conflict"),
                dcc.Dropdown(
                    id="selected-country",
                    options=[
                        {"label": k, "value": country_code_dict[k]}
                        for k in country_code_dict
                    ],
                    value="AFG",
                ),
                html.Div(id="sidebar-summary",
                    children="",
                )
            ],
        ),
        # html.Div(
        #     className="grid-item grid-map-component",
        #     style={"grid-area": "map"},
        #     children=[
        #         dcc.Graph(id="main-map")
        #     ]
        # ),
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
                        ),
                    ],
                ),
                dcc.Graph(id="selected-chart"),
            ],
        ),
        # SpaceTime clustering charts
        html.Div(
            className="grid-item grid-graph-component",
            style={"grid-area": "3d-scatter"},
            children=[
                html.H4("Space-time clustering"),
                 html.Button("About this chart", type="button", className="collapsible"),
                html.Div(children=[
                    html.P(
                    '''
                    This component clusters the conflict data of the country undergoing an HMI using the Hierarchical Clustering algorithm and plots it in an interactive 3-D chart. The top-left slider controls the emphasis on spatial distances versus temporal distances when clustering the data, and the slider on the right controls the number of clusters the algorithm generates. Clicking on any point in the 3-D chart will update the map above and the scatter plot below to show only the data of the specific cluster to which the clicked point belongs. Finally, the checkbox in the bottom-left of the 3-D chart component toggles the display of horizontal planes which indicate the start and the end of the HMI for the studied intervention.
                    ''')
                ], className="content"),
                html.Div(
                    className="side-by-side-input",
                    children=[
                        html.Div(
                            [
                                html.Label(
                                    "Select spatial vs. temporal weighting for cluster generation:"
                                ),
                                html.P(
                                    "*(1: pure spatial, 3: medium-spatial medium-temporal, 5: pure temporal)*"
                                ),
                                dcc.Slider(
                                    id="cluster-weighting",
                                    min=1,
                                    max=5,
                                    marks={i: str(i) for i in range(1, 6)},
                                    value=3,
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.Label("Select number of clusters:"),
                                dcc.Markdown(
                                    id = "cluster-number-text",
                                    children = ["Number of clusters: "]
                                ),
                                dcc.Slider(
                                    id="cluster-number-slider",
                                    min=1,
                                    max=40,
                                    step=1,
                                    value=10,
                                    marks = {
                                        1: '1',
                                        10: '10',
                                        20: '20',
                                        30: '30',
                                        40: '40'
                                    }
                                ),
                            ]
                        ),
                    ],
                ),
                dcc.Graph(id="3d-scatter-plot", 
                            style={'height': '40em'}),
                dcc.Checklist(
                    id="showOrHideHMIPlanes",
                        options=[
                            {'label': 'Show Start/End HMI', 'value': 'show'}
                        ],
                        value=[]
                    )  
            ],
            
        ),
        html.Div(
            className="grid-item grid-graph-component",
            style={"grid-area": "cluster-scatter-timeline"},
            children=[
                html.H4("Cluster Over Time"),
                dcc.Markdown(children="Cluster number: 1", id="cluster-number"),
                dcc.Graph(id="cluster-scatter-timeline"),
            ],
        ),
        html.Div(
            className="grid-item grid-map-component",
            style={"grid-area": "cluster-scatter-geographic"},
            children=[
                html.H4("Cluster in Space", className="overlay-text"),
                dcc.Graph(id="cluster-scatter-geographic"),
            ],
        ),
        #################### SOCIOECONOMIC ELEMENTS ####################
        html.Div(
            className="grid-item grid-graph-component",
            style={"grid-area": "se-factors"},
            children=[
                html.H4("Socioeconomic Indicators"),
                html.Div(
                    className="side-by-side-input",
                    children=[
                        html.Div(
                            [
                                html.H6("Select category"),
                                html.Div(
                                        dcc.Dropdown(
                                            id="categories-dropdown",
                                            options=[{'label': k, 'value': k} for k in all_se_options.keys()],
                                            value="Demography"
                                        )
                                    )
                            ]
                        ),
                        html.Div(
                            children=[
                                html.H6("Select indicator within the category"),
                                html.Div(
                                    children= [
                                        dcc.Dropdown(
                                                id="indicators-dropdown",
                                                value = "Population, total"
                                        )
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
                dcc.Graph(id="indicator-chart"),
            ],
        ),
        html.Div(
            className="grid-item grid-st-component",
            style={"gridArea": "st-knox"},
            children=[
                html.H4("Space-time contingency tables"),
                html.Button("About this chart", type="button", className="collapsible"),
                html.Div(children=[
                    html.P(
                    '''
                    These Knox tables compare the observed space-time correlations observed in event data, in terms of the time between different events, and the distances between different events. A higher Knox ratio for a given square (i.e. spatial and temporal distance between events) indicates a higher observed correlation at this scale than the expected value for a randomised, uncorrelated system. Thus a green or yellow color indicates that there is a strong space-time correlation between events separated by a certain spatial or temporal distance.
                    '''),
                    html.P(
                        '''
                        Note that some tables may be empty due to a lack of recorded conflict events before or after intervention.
                        '''
                    )
                ], className="content"),
               
                # Not so pretty workaround to get the boxes squared
                html.Div(className="fixed-ratio-box", children=[
                    html.Div(className="fixed-ratio-inside", children=[
                        dcc.Graph(id="st-knox-tables", style={'height': 'inherit'})
                        ]
                    )
                ]),
            ],
        ),
    ],
    className="grid-container",
)

######################################################
# Sidebar elements
######################################################

@app.callback(
        Output('sidebar-summary', 'children'),
        Input('selected-country', 'value')
)
def update_sidebar(country):
    #http://www.humanitarian-military-interventions.com/wp-content/uploads/2019/08/PRIF-data-set-HMI-codebook-v1-14.pdf
    df = conflict_dict[country]["hmi_df"].to_dict()
    sb = sidebar_generator(df)
    return sb

######################################################
# Base conflict events/severity scatterplot
######################################################

@app.callback(
    Output("selected-chart", "figure"),
    Input("selected-country", "value"),
    Input("chart-type", "value"),
    Input("yaxis-type", "value"),
)
def update_conflict_graph(country, chart_type, yaxis_type):
    # create the bubble plot
    if chart_type == available_charts[0]:
        max = conflict_dict[country]["monthly_casualties_df"]["events"].max()
        fig = px.scatter(
            conflict_dict[country]["monthly_casualties_df"],
            x="Month",
            y="events",
            size="marker_size",
            # hover_template='%{y:.0f}days <br>'
            hover_name="Month",  # formatting becomes weird for the heading!
            hover_data={
                "marker_size": False,
                "casualties": True,  # tried to rename this to
            },
        )
    else:
        max = conflict_dict[country]["monthly_casualties_df"]["casualties"].max()
        fig = px.scatter(
            conflict_dict[country]["monthly_casualties_df"], x="Month", y="casualties"
        )

    fig.update_layout(
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        hovermode="closest",
        transition_duration=500,
    )
    fig.update_yaxes(
        title="Number of recorded events per month",
        range=[0, max] if yaxis_type == "Linear" else [0, log(max)],
        type="linear" if yaxis_type == "Linear" else "log",
    )

    start = dict(txt='Start HMI', date=conflict_dict[country]["hmi_df"]["HMISTART"])
    end = dict(txt='End Hmi', date=conflict_dict[country]["hmi_df"]["HMIEND"])

    for d in [start, end]:
        if d['date'] == 0:
            continue
        fig.add_annotation(
            x=d['date'],
            y=0,
            ax=d['date'],  # arrows' tail
            ay=max if yaxis_type == "Linear" else log(max),
            text=d['txt'],
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
        )

    return fig


######################################################
# 3D scatterplot clusters
######################################################

@app.callback(
    Output("3d-scatter-plot", "figure"),
    Input("selected-country", "value"),
    Input("cluster-weighting", "value"),
    Input("cluster-number-slider", "value"),
    Input("showOrHideHMIPlanes", "value")
)
def update_3d_graph(country, cluster_weighting, n_clusters, show_hide_planes):
    # Drop cols & create date instances
    # all of this data processing is not necessary unless we change country!
    df_clean = conflict_dict[country]["conflict_df"].loc[
        :, ["date_start", "best", "latitude", "longitude", "side_a", "side_b"]
    ]
    df_clean["date"] = pd.to_datetime(df_clean["date_start"])
    df_clean = df_clean.rename(columns={"best": "casualties"})

    # Calculate days from earliest event for faster comparison
    first_date = df_clean["date"].min() 
    df_clean["years"] = (df_clean["date"] - first_date).dt.days / (365) 

    # Calculate location of start and end of hmi vs. earliest event
    hmi_start = (pd.to_datetime(conflict_dict[country]["hmi_df"]["HMISTART"]) - first_date).days / (365) 
    hmi_end = (pd.to_datetime(conflict_dict[country]["hmi_df"]["HMIEND"]) - first_date).days / (365) 

    # grab relevant linkage matrix
    linkage_matrix = conflict_dict[country]["linkage"][str(cluster_weighting)]

    df_clean["c"] = fcluster(linkage_matrix, n_clusters, criterion="maxclust")
    df_clean["Cluster"] = df_clean["c"].apply(str)

    # create the full scatter plot
    fig_3d = px.scatter_3d(
        df_clean,
        x="latitude",
        y="longitude",
        z="years",
        color="Cluster",
        opacity=0.9,
        size_max=1,
        # '<br><b>X</b>: %{x}<br>'+
        # '<b>%{text}</b>',
        hover_data={"Cluster": True, "side_a": True, "side_b": True, "date": True},
    )

    # for fignum in range(len(fig_3d.data)):
    #     fig_3d.data[fignum].update(hovertemplate=
    #     '<b>Cluster</b> %{customdata[0]}'+
    #     'Lat: %{x:.2f}, Lon: %{y:.2f}')


    if show_hide_planes == ['show']:
        x = pd.Series([df_clean['latitude'].min(), df_clean['latitude'].min(), df_clean['latitude'].max(), df_clean['latitude'].max()])
        y = pd.Series([df_clean['longitude'].min(), df_clean['longitude'].max(), df_clean['longitude'].max(), df_clean['longitude'].max()])
        
        z_start = hmi_start * np.ones((4,4))
        z_end = hmi_end * np.ones((4,4))

        cSurface = np.zeros(shape=z_start.shape)    
        cScale = [[0, 'rgba(0,0,0)'], 
                [1, 'rgba(0,0,0)']]

        fig_3d.add_trace(go.Surface(x=x, y=y, z=z_start, opacity=.5, surfacecolor=cSurface, colorscale=cScale, showscale=False, name="Start Intervention"))
        if(conflict_dict[country]["hmi_df"]["HMIEND"]):
            fig_3d.add_trace(go.Surface(x=x, y=y, z=z_end, opacity=.5, surfacecolor=cSurface, colorscale=cScale, showscale = False, name="End Intervention"))

    fig_3d.update_layout(margin=dict(l=30, r=20, b=30, t=20, pad=4))
    fig_3d.update_layout(scene_aspectmode="cube")#_aspectratio=dict(x=2, y=2, z=1))

    return fig_3d


######################################################
# Update time & Geographic scatter plot of selected cl
######################################################

@app.callback(
    Output("cluster-scatter-timeline", "figure"),
    Output("cluster-scatter-geographic", "figure"),
    Output("cluster-number-text", "children"),
    Output("cluster-number", "children"),
    Input("selected-country", "value"),
    Input("cluster-weighting", "value"),
    Input("cluster-number-slider", "value"),
    Input("3d-scatter-plot", "clickData"),
)
def update_cluster_charts(country, cluster_weighting, n_clusters, clickData):
    df_clean = conflict_dict[country]["conflict_df"].loc[
        :, ["date_start", "best", "latitude", "longitude", "side_a", "side_b"]
    ]
    df_clean["date"] = pd.to_datetime(df_clean["date_start"])
    df_clean = df_clean.rename(columns={"best": "casualties"})

    # grab relevant linkage matrix
    linkage_matrix = conflict_dict[country]["linkage"][str(cluster_weighting)]
    df_clean["cluster"] = fcluster(linkage_matrix, n_clusters, criterion="maxclust")

    
    # create the time chart
    if clickData:
        # print(int())
        cluster_id = int(clickData["points"][0]['customdata'][0])
        df = df_clean[df_clean.cluster == cluster_id]
    else:
        cluster_id = "*"
        df = df_clean

    scatter_timeline = px.scatter(df, x="date", y="casualties")

    # print(df_clean[df_clean.cluster == cluster_id])
    scatter_geographic = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        zoom=5,
        size="casualties",
        mapbox_style="light",
    )
    scatter_geographic.update_layout(autosize=False, margin=dict(t=0, b=0, l=0, r=0))
    scatter_geographic.update_layout(showlegend=False)
            
    cluster_number_text = "**{}** clusters generated".format(n_clusters)

    cluster_text = """
    Cluster number: **{}**\n
    | Number of points | Avg. cas. per event | Stdev. of cas. per event |
    |  :--: |  :--: |  :--: |
    |   {}  |   {}  |   {}  |
    """.format(
            str(cluster_id),
            str(len(df_clean[df_clean.cluster == cluster_id])), 
            str(df_clean[df_clean.cluster == cluster_id].casualties.mean()),
            str(df_clean[df_clean.cluster == cluster_id].casualties.std())
        )


    return [scatter_timeline, scatter_geographic, cluster_number_text, cluster_text]


######################################################
# Socioeconomic charts
######################################################

# change selectable indicators based on selected category
@app.callback(
    Output('indicators-dropdown', 'options'),
    Input('categories-dropdown', 'value'))
def set_options(selected_category):
    return [{'label': i, 'value': i} for i in all_se_options[selected_category]]

# update selected indicator
@app.callback(
    Output('indicators-dropdown', 'value'),
    Input('indicators-dropdown', 'options'))
def set_value(available_options):
    return available_options[0]['value']

@app.callback(
    Output('indicator-chart', 'figure'),
    Input('selected-country', 'value'),
    Input('indicators-dropdown', 'value'),
)
def update_se_graph_variables(country, selected_indicator):
    se_df = conflict_dict[country]['se_df']
    countries_to_hide_dict = {
        "AFG": ["Pakistan", "Iran, Islamic Rep.", "Turkmenistan", "Uzbekistan", "Tajikistan"],
        "IRQ": ["Iran, Islamic Rep.", "Syrian Arab Republic", "Jordan", "Turkey", "Saudi Arabia", "Kuwait"],
        "SOM": ["Kenya", "Ethiopia", "Djibouti"],
        "LKA": ["India", "Bangladesh", "Pakistan"]
    }
    
    fig = px.line(se_df, # update this to the dict file path
                x="Year",
                y=selected_indicator,
                color="Country")

    
    #As default, hide neighbouring countries
    fig.for_each_trace(lambda trace: trace.update(visible="legendonly") 
                    if trace.name in countries_to_hide_dict[country] else ())


    mx = 0
    for f in fig.data:
        mxt = max(f['y'])
        if mxt > mx:
            mx = mxt

    fig.update_layout(transition_duration=500)


    start_year = int(conflict_dict[country]["hmi_df"]["HMISTART"].strftime("%Y"))
    start_month = int(conflict_dict[country]["hmi_df"]["HMISTART"].strftime("%m"))/11
    start = dict(txt="Start HMI", date=start_year+start_month)

    try: 
        end_year = int(conflict_dict[country]["hmi_df"]["HMIEND"].strftime("%Y"))
        end_month = int(conflict_dict[country]["hmi_df"]["HMIEND"].strftime("%m"))/11
    except:
        end_year = 0
        end_month = 0
    end = dict(txt="End HMI", date=end_year+end_month)
        
    

    for d in [start, end]:
        if d['date'] == 0:
            continue
        fig.add_annotation(
            x=d['date'],
            ax=d['date'], 
            xref="x",
            axref="x",

            y=0,
            ay=mx,
            yref="y",
            ayref="y",

            text=d['txt'],
            showarrow=True,
            arrowwidth=1,          

        )  

        

    return fig   


######################################################
# ST Contingency / Knox Correlation Tables 
######################################################

@app.callback(Output("st-knox-tables", "figure"), Input("selected-country", "value"))
def update_knox_tables(country, resolution="Lowres"):
    # print(country)
    # Fetch data
    df_dur = knox_data[country][resolution]["During"]
    df_pri = knox_data[country][resolution]['Prior']
    df_aft = knox_data[country][resolution]["After"]



    fig = make_subplots(
        # rows=0,
        cols=3,
        shared_xaxes=True,
        shared_yaxes=True,
        start_cell="top-left",
        subplot_titles=["Prior to HMI", "During HMI", "After HMI"],
        x_title="Distance (km) →",
        y_title="Timedifference (days) →",
    )

    fig.update_layout(margin=dict(l=60, r=20, b=60, t=20, pad=4))

    for i, df in enumerate([df_pri, df_dur, df_aft]):
        if isinstance(df, pd.DataFrame):
            z = df.values.tolist()
            x = df.columns.tolist()
            y = df.index.tolist()
        else:
            try:
                z = None
                x = df_dur.columns.tolist()
                y = df_dur.index.tolist()
            except:
                z = None
                x = df_aft.columns.tolist()
                y = df_aft.index.tolist()

        fig.add_trace(
            go.Heatmap(
                z=z,
                x=x,
                y=y,
                zmin=0.5,
                zmax=2.5,
                colorbar=dict(title="Ratio<br>observed/MC"),
                colorscale="viridis",
                hovertemplate='%{x:.0f} km <br>'+
                                '%{y:.0f} days <br>'+
                                '%{z:.2f} knox ratio'
    #     '<br>Cluster</br> %{customdata[0]}'+
    #     'Lat: %{x:.2f}, Lon: %{y:.2f}')
            ),
            row=1,
            col=i + 1,
        )

    return fig


if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=5000, use_reloader=True)
