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

# import variables from separate data processing file
from data_preparation import generate_conflict_dict, generate_relevant_entries_dict

conflict_dict = generate_conflict_dict()
relevant_entries_dict = generate_relevant_entries_dict()

# Load knox tables data
with open(r"Production Data/Knox tables/knox_tables.pickle", "rb") as handle:
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
            className="grid-item grid-text-component grid-text-sidebar",
            style={"grid-area": "side"},
            children=[
                html.H2("[DSP dashboard concept]"),
                html.Label("Select conflict"),
                dcc.Dropdown(
                    id="selected-country",
                    options=[
                        {"label": k, "value": country_code_dict[k]}
                        for k in country_code_dict
                    ],
                    value="AFG",
                ),
                html.Div(
                    children=[
                        html.H3("Basic Summary"),
                        dcc.Markdown(
                            id="basic-summary",
                            children="Additional information summarizing the intervention.",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.H3("Description of approval/motivations:"),
                        dcc.Markdown(
                            id="approval-motivations",
                            children="Additional information capturing the motivations/approval of the intervention.",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.H3("Basic Intervention Characteristics:"),
                        dcc.Markdown(
                            id="intervention-characteristics",
                            children="Basic intervention characteristics.",
                        ),
                    ]
                ),
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
                dcc.Graph(id="3d-scatter-plot"),
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
                                        {"label": i, "value": i}
                                        for i in available_indicators
                                    ],
                                    value="GDP per capita (current US$)",
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.H6("Secondary axis variable"),
                                dcc.Dropdown(
                                    id="secondary-yaxis",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in available_indicators
                                    ],
                                    value="Electoral democracy index (v2x_polyarchy)",
                                ),
                            ],
                        ),
                    ],
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
                        for value in range(
                            conflict_df.year.min(), conflict_df.year.max(), 2
                        )
                    },
                ),
            ],
        ),
        html.Div(
            className="grid-item grid-st-component",
            style={"gridArea": "st-knox"},
            children=[
                html.H4("Space-time contingency tables"),

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

@app.callback(Output("basic-summary", "children"), Input("selected-country", "value"))
def update_basic_summary(country):
    hmi_df = conflict_dict[country]["hmi_df"]
    relevant_entries = [
        "HMISTART",
        "HMIEND",
        "TARGET",
        "INTERVEN1",
        "INTERVEN2",
        "INTERVEN3",
    ]
    text = ""
    for entry in relevant_entries:
        if hmi_df[entry] != -88:
            text += "\n#### {}\n\n{}\n".format(
                relevant_entries_dict[entry], hmi_df[entry]
            )

    return text


@app.callback(
    Output("approval-motivations", "children"), Input("selected-country", "value")
)
def update_approval_motivations(country):
    hmi_df = conflict_dict[country]["hmi_df"]
    relevant_entries = ["ISSUE", "UNSC", "REGIOORG", "GOVTPERM", "CONTRA4", "CONTRA5"]
    text = ""
    for entry in relevant_entries:
        if hmi_df[entry] != -88:
            text += "\n**{}**\n\n{}\n".format(
                relevant_entries_dict[entry], hmi_df[entry]
            )

    return text


@app.callback(
    Output("intervention-characteristics", "children"),
    Input("selected-country", "value"),
)
def update_intervention_characteristics(country):
    hmi_df = conflict_dict[country]["hmi_df"]
    relevant_entries = ["TATROOP", "GROUNDFO", "GROUNDNO", "ACTIVE", "FORCE"]
    text = ""
    for entry in relevant_entries:
        if hmi_df[entry] != -88:
            text += "\n**{}**\n\n{}\n".format(
                relevant_entries_dict[entry], hmi_df[entry]
            )

    return text


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

    # for x in 
    start = dict(txt='Start HMI', date=conflict_dict[country]["hmi_df"]["HMISTART"])
    end = dict(txt='End Hmi', date=conflict_dict[country]["hmi_df"]["HMIEND"])

    for d in [start, end]:
        fig.add_annotation(
            x=d['date'],
            y=0,
            ax=d['date'],  # arrows' tail
            ay=max if yaxis_type == "Linear" else log(max),
            text=d['txt'],
            showarrow=True,
            # textposition="Top center",
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
    print(show_hide_planes)
    # Drop cols & create date instances
    # all of this data processing is not necessary unless we change country!
    df_clean = conflict_dict[country]["conflict_df"].loc[
        :, ["date_start", "best", "latitude", "longitude", "side_a", "side_b"]
    ]
    df_clean["date"] = pd.to_datetime(df_clean["date_start"])
    df_clean = df_clean.rename(columns={"best": "casualties"})

    # Calculate days from earliest event for faster comparison
    first_date = df_clean["date"].min()
    df_clean["days_from_earliest"] = (df_clean["date"] - first_date).dt.days

    # Calculate location of start and end of hmi vs. earliest event
    hmi_start = (pd.to_datetime(conflict_dict[country]["hmi_df"]["HMISTART"]) - first_date).days
    hmi_end = (pd.to_datetime(conflict_dict[country]["hmi_df"]["HMIEND"]) - first_date).days

    # grab relevant linkage matrix
    linkage_matrix = conflict_dict[country]["linkage"][str(cluster_weighting)]

    df_clean["c"] = fcluster(linkage_matrix, n_clusters, criterion="maxclust")
    df_clean["Cluster"] = df_clean["c"].apply(str)

    # create the full scatter plot
    full_scatter_plot = px.scatter_3d(
        df_clean,
        x="latitude",
        y="longitude",
        z="days_from_earliest",
        color="Cluster",
        opacity=0.9,
        size_max=2,
        # size=5,
        # symbol="c-str",
        hover_data={"Cluster": True, "side_a": True, "side_b": True, "date": True},
    )

    if show_hide_planes == ['show']:
        x = pd.Series([df_clean['latitude'].min(), df_clean['latitude'].min(), df_clean['latitude'].max(), df_clean['latitude'].max()])
        y = pd.Series([df_clean['longitude'].min(), df_clean['longitude'].max(), df_clean['longitude'].max(), df_clean['longitude'].max()])
        
        length_data = len(y)
        z_start = hmi_start * np.ones((4,4))
        z_end = hmi_end * np.ones((4,4))

        cSurface = np.zeros(shape=z_start.shape)    
        cScale = [[0, 'rgba(0,0,0)'], 
                [1, 'rgba(0,0,0)']]

        full_scatter_plot.add_trace(go.Surface(x=x, y=y, z=z_start, opacity=.5, surfacecolor=cSurface, colorscale=cScale, showscale=False, name="Start Intervention"))
        if(conflict_dict[country]["hmi_df"]["HMIEND"]):
            full_scatter_plot.add_trace(go.Surface(x=x, y=y, z=z_end, opacity=.5, surfacecolor=cSurface, colorscale=cScale, showscale = False, name="End Intervention"))



    full_scatter_plot.update_layout(margin=dict(l=30, r=20, b=30, t=20, pad=4))
    
    return full_scatter_plot


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

@app.callback(
    Output("indicator-chart", "figure"),
    Input("selected-country", "value"),
    Input("primary-yaxis", "value"),
    Input("secondary-yaxis", "value"),
    Input("indicator-range", "value"),
)
def update_se_graph_variables(country, primary_yaxis, secondary_yaxis, indicator_range):

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # dataframe limited to the year range
    se_df = conflict_dict[country]["se_df"]
    dff = se_df[(se_df.Year >= indicator_range[0]) & (se_df.Year <= indicator_range[1])]

    fig.add_trace(
        go.Scatter(
            x=dff["Year"], y=dff[primary_yaxis], name=primary_yaxis, mode="lines"
        ),
        secondary_y=False,
    )

    fig.update_yaxes(title_text=primary_yaxis, secondary_y=False)

    fig.add_trace(
        go.Scatter(
            x=dff["Year"], y=dff[secondary_yaxis], name=secondary_yaxis, mode="lines"
        ),
        secondary_y=True,
    )

    fig.update_yaxes(title_text=secondary_yaxis, secondary_y=True)

    fig.update_layout(
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        hovermode="closest",
        legend_x=0.01,
        legend_y=1,
        transition_duration=500,
    )

    return fig


######################################################
# ST Contingency / Knox Correlation Tables 
######################################################

@app.callback(Output("st-knox-tables", "figure"), Input("selected-country", "value"))
def update_knox_tables(country):
    # Fetch data
    df_dur = knox_data[country]["During"]
    df_pri = None  # knox_data[country]['Prior']
    df_aft = knox_data[country]["After"]

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

    fig.update_layout(margin=dict(l=30, r=20, b=30, t=20, pad=4))

    for i, df in enumerate([df_pri, df_dur, df_aft]):
        if isinstance(df, pd.DataFrame):
            z = df.values.tolist()
            x = df.columns.tolist()
            y = df.index.tolist()
        else:
            z = None
            x = df_dur.columns.tolist()
            y = df_dur.index.tolist()

        fig.add_trace(
            go.Heatmap(
                z=z,
                x=x,
                y=y,
                zmin=0.75,
                zmax=1.75,
                colorbar=dict(title="Title"),
                colorscale="viridis",
            ),
            row=1,
            col=i + 1,
        )

    return fig


if __name__ == "__main__":
    app.run_server(debug=False, port=3008)
