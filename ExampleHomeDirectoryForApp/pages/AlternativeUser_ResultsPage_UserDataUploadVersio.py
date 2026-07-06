#Page to show tables with raw + filtered data

import dash
from dash import html, callback, Input, Output, dash_table, dcc, State, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
import math
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import base64
import io
import datetime

import ReportFunctions

#TODO: Update for each individual user account
accountIndexPage = "/AddYourOwnAlternativeAccountHef"
#TODO: Update for each individual page
page_name = "User Uploads Data Results Example"
        
dash.register_page(__name__,  
                   name = page_name,
                   path = "/AddOwnAlternativeResultsPath", 
                   order = 0
                   )

#TODO: Update for each individual project
project_no = "ProjectNo"
#TODO: Use replace all to replace _UPLOADDATA with actual project number

#Need to make sure each report has unique functions names when deployed with others

p_value_data = pd.DataFrame(data={'p-value': [0.05, 0.01, 0.001], 
                                  'p-value(-log10)': [1.3, 2, 3]})

rawData_tab = dbc.Card(
    dbc.CardBody(
        [
            html.P("Images of your graphs and plots can be directly downloaded when you view them in their respective pages of this report. Simply hover your mouse cursor over your graph and select the camera icon to “Download plot as a png”."),
            html.H5("Distribution of Feature Intensities", 
                    style={'textAlign': 'center'}),
            html.P("View the histogram distribution of the frequency of raw metabolite intensities across your selected samples. "),
            dbc.Row([
                dbc.Col([
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "histrogram_raw_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download Raw data", 
                                id = "btn-download-raw-transposed-inTab_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    ],
                    lg = {"size":8, "offset":2})
                ]),
            html.H5("Raw Data Table", 
                    style={'textAlign': 'center'}),
            html.P("View the raw data metabolite peak intensities for each sample and group (“Label”). Note: the data processing software automatically assigns metabolites not detected in a particular sample as 0.001.", className="card-text"),
            dbc.Spinner(
                children=[
                    html.Div(id='display_subset_raw_tabs_UPLOADDATA'),
                    ],
                size = "lg", 
                color = "primary", 
                fullscreen = True
                ),
        ]
    ),
    className="mt-3",
)

normData_tab = dbc.Card(
    dbc.CardBody(
        [
            html.P("Images of your graphs and plots can be directly downloaded when you view them in their respective pages of this report. Simply hover your mouse cursor over your graph and select the camera icon to “Download plot as a png”."),
            html.H5("Distribution of Feature Intensities", 
                    style={'textAlign': 'center'}),
            html.P("View the histogram distribution of the frequency of normalised metabolite intensities across your selected samples. Note: these should have an overall normal/Gaussian distribution, appropriate for performing statistical analyses with."),
            dbc.Row([
                dbc.Col([
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "histogram_norm_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download Normalised data", 
                                id = "btn-download-norm-inTab_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    ],
                    lg = {"size":8, "offset":2})
                ]),
            html.H5("Normalised Data Table", 
                    style={'textAlign': 'center'}),
            html.P("View the normalised metabolite peak intensities for each sample and group (“Label”). Note: if any metabolites are not detected in your sample selection, these are removed from the selected dataset as those would otherwise introduce “Divide by 0” errors during the Pareto scaling.", className="card-text"),
            dbc.Spinner(
                children=[
                    html.Div(id='display_subset_tabs_UPLOADDATA'),
                    ],
                size = "lg", 
                color = "primary", 
                fullscreen = True
                ),
        ]
    ),
    className="mt-3",
)

PCA_tab = dbc.Card(
    dbc.CardBody(
        [
            html.Br(),
            html.H4("Principal Component Analysis (PCA)", 
                    style={'textAlign': 'center'}),
            dcc.Markdown("""PCA is an *unsupervised* linear dimensionality reduction technique. Simply, Scikit Learn’s PCA functions are used to convert the correlations/non-correlations in the normalised metabolite intensity data into Principal Components that can be viewed in two dimensions. Samples that are highly correlated will cluster together and those that are not will be spread apart from each other. Each Component is ranked: differences along the first Principal Component axis (PC1) are more important that the differences along the second principal component axis (PC2). """),
            html.P("Images of your graphs and plots can be directly downloaded when you view them in their respective pages of this report. Simply hover your mouse cursor over your graph and select the camera icon to “Download plot as a png”."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H5("PCA scores plot", 
                            style={'textAlign': 'center'}),
                    html.P("View how each of your selected samples are similar/dissimilar to each other. The percentages on each axis represent the variation ratio of each component. The circles represent 95% confidence intervals for the samples in each group."),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_scores_plot_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download PCA scores data", 
                                id = "btn-download-pca-scores-inTab_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    ], lg={"size":6}
                    ), 
                dbc.Col([
                    html.H5("PCA loadings plot", 
                            style={'textAlign': 'center'}),
                    html.P("View the metabolites that are driving the variation observed in the Scores plot. Hover over the data points to show metabolites. You can select these datapoints to view their raw and normalised abundances in the metabolite selection plots below."),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_loadings_plot_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download PCA loadings data", 
                                id = "btn-download-pca-loadings-inTab_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    ], 
                    lg={"size":6}
                    ),
                ]), 
            dbc.Row([
                    html.H5("Examine PCA Loadings' plot metabolite", 
                            style={'textAlign': 'center'}),
                    html.P("Select a metabolite data point from the loadings plot to see its average peak intensity across the sample groups (error bars indicate standard deviation)", 
                           ),
                ]),
            dbc.Row([
                dbc.Col([
                    html.H5("Raw data", style={'textAlign': 'center'}),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_metabolite_select_raw_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    ], 
                    lg={"size":6}
                    ),
                dbc.Col([
                    html.H5("Normalised data", style={'textAlign': 'center'}),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_metabolite_select_norm_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    ], 
                    lg={"size":6}
                    ),
                ]), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H5("VIP score (top 50)", style={'textAlign': 'center'}),
                    html.P("View the top 50 ranked metabolites that drive variation along the first Principal Component axis (PC1) based on their Variable Importance Point (VIP) score. The red dashed line denotes the conventional significance threshold, where VIP scores above 1.0 are considered significant."),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_vip_plot_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download PCA VIP Scores", 
                                id = "btn-download-pca-vip-scores-inTab_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    ], 
                    lg={"size":6}
                    ),
                dbc.Col([
                    html.H5("Scaled group average intensity", style={'textAlign': 'center'}),
                    html.P(dcc.Markdown("For each of the metabolites in the VIP score plot, view their average intensity across each of your selected sample groups. Note: the colours in the heatmap are scaled by the average intensity for each **metabolite independently**. Therefore, this allows a comparison of intensities *within* rows but not *between* rows. ")
                           ),
                    html.Br(),
                    html.Br(),
                    html.Br(), #Added in to make graphs level in lg screen
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_group_avg_heatmap_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    ], 
                    lg={"size":6}
                    ),
                ]), 
            html.Br(),
#Metabolite selection (PCA)
            dbc.Row([
                    html.H5("Examine selected metabolites", 
                            style={'textAlign':'center'}), 
                    html.P("Select metabolites from the dropdown list to view their intensities across your sample groups. You can select between Bar, Box, or Violin plots for both your raw and normalised datasets. Bar Plot: error bars indicate standard deviation. For the raw data, you can also decide to view it with a linear or log (base 10) y-axis. Note: if there are values equal to or less than 0 present, this will automatically cause the log10 y-axis to become infinite."), 
                    dcc.Dropdown(id = "pca_any_metab_selection_UPLOADDATA", multi = True)
                ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Update selected metabolite plots", 
                                id = "btn-update-pca-any-metab-sele_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    ])
                ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H5("Raw Data", style = {'textAlign':'center'}), 
                    html.P("Plot Type:"),
                    dcc.RadioItems(
                        id='pca_raw_plot_type_sele_UPLOADDATA', 
                        options=['Bar Plot', 'Box Plot', 'Violin Plot'],
                        value='Bar Plot'
                        ),
                    html.Br(), 
                    html.P("Y-axis scale:"),
                    dcc.RadioItems(
                        id='pca_raw_plot_yaxis_sele_UPLOADDATA', 
                        options=['Linear', 'Log10'],
                        value='Linear'
                        ),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_any_metab_raw_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    ], 
                    lg={"size":6}
                    ),
                dbc.Col([
                    html.H5("Normalised Data", style = {'textAlign':'center'}), 
                    html.P("Plot Type:"),
                    dcc.RadioItems(
                        id='pca_norm_plot_type_sele_UPLOADDATA', 
                        options=['Bar Plot', 'Box Plot', 'Violin Plot'],
                        value='Bar Plot'
                        ),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(), #Added in to make graphs align in lg screen
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_any_metab_norm_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    ], 
                    lg={"size":6}
                    )
                ]),
            dbc.Row([
                dbc.Col([
                    html.H5("Raw Data for each sample", style = {'textAlign':'center'}),
                    html.P("View the raw intensity of each metabolite selected above for each individual sample you have selected for analysis (as opposed to the group averages). The horizontal lines correspond to the total average metabolite intensity for each metabolite selected.", style = {'textAlign':'center'}), 
                    html.P("Use the Y-axis scale buttons above to alternate between a linear and logarithmic Y-axis.", style = {'textAlign':'center'})
                    ]), 
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_any_metab_eachSample_raw_UPLOADDATA")
                            ],
                        # size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                ])
        ]
    ),
    className="mt-3",
)

PLSDA_tab = dbc.Card(
    dbc.CardBody(
        [
            html.Br(),
            html.H4("Partial Least Squared Discriminant Analysis (PLS-DA)", 
                    style={'textAlign': 'center'}),
            dcc.Markdown("""PLS-DA is a *supervised* dimensionality reduction technique. Here, information about the sample groupings is used with the normalised metabolite intensity data in Scikit Learn’s PLS Regression functions to cross-validate and select an optimal number of components for classification. Samples that are highly correlated will cluster together and those that are not will be spread apart from each other. **Note**: It is possible with PLS-DA to get a higher variation on Component 2 compared to Component 1."""),
            html.P("Images of your graphs and plots can be directly downloaded when you view them in their respective pages of this report. Simply hover your mouse cursor over your graph and select the camera icon to “Download plot as a png”."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H5("PLS-DA scores plot", 
                            style={'textAlign': 'center'}),
                    html.P("View how each of your selected samples are similar/dissimilar to each other. The percentages on each axis represent the variation ratio of each component. The circles represent 95% confidence intervals for the samples in each group. "),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "interactive_plsda_plot_2D_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download PLS-DA scores data", 
                                id = "btn-download-plsda-scores-inTab_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    ], lg = {"size":6}
                    ), 
                dbc.Col([
                    html.H5("PLS-DA loadings plot", 
                            style={'textAlign': 'center'}),
                    html.P("View the metabolites that are driving the variation observed in the Scores plot. Hover over the data points to show metabolites. Select these datapoints to view their raw and normalised abundances in the metabolite selection plots below."),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "plsda_loadings_plot_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download PLS-DA loadings data", 
                                id = "btn-download-plsda-loadings-inTab_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    ], 
                    lg = {"size":6}
                    ),
                ]), 
            dbc.Row([
                html.H5("Examine metabolite", 
                        style={'textAlign': 'center'}),
                html.P("Select a metabolite data point from the loadings plot to see its average peak intensity across the sample groups (error bars indicate standard deviation)", 
                       style={'textAlign': 'center'}),
                ]),
            dbc.Row([
                dbc.Col([
                    html.H5("Raw data", style={'textAlign': 'center'}),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "plsda_metabolite_select_raw_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    ], 
                    lg={"size":6}
                    ),
                dbc.Col([
                    html.H5("Normalised data", style={'textAlign': 'center'}),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "plsda_metabolite_select_norm_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    ], 
                    lg={"size":6}
                    ),
                ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H5("VIP score (top 50)", style={'textAlign': 'center'}),
                    html.P("View the top 50 ranked metabolites that drive variation along the Component axis 1 based on their Variable Importance of Projection (VIP) score. The red dashed line denotes the conventional significance threshold, where VIP scores above 1.0 are considered significant."),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "plsda_vip_plot_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download PLS-DA VIP Scores", 
                                id = "btn-download-plsda-vip-scores-inTab_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    ], 
                    lg={"size":6}
                    ),
                dbc.Col([
                    html.H5("Scaled group average intensity", style={'textAlign': 'center'}),
                    html.P(dcc.Markdown("For each of the metabolites in the VIP score plot, view their average intensity across each of your selected sample groups. Note: the colours in the heatmap are scaled by the average intensity for each **metabolite independently**. Therefore, this allows a comparison of intensities *within* rows but not *between* rows.")
                           ),
                    html.Br(),
                    html.Br(),
                    html.Br(), #Added in to make graphs level in lg screen
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "plsda_group_avg_heatmap_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    ], 
                    lg={"size":6}
                    ),
                ]), 
            html.Br(),
#Metabolite selection (PLS-DA)
            dbc.Row([
                    html.H5("Examine selected metabolites", 
                            style={'textAlign':'center'}), 
                    html.P("Select metabolites from the dropdown list to view their intensities across your sample groups. You can select between Bar, Box, or Violin plots for both your raw and normalised datasets. Bar Plot: error bars indicate standard deviation. For the raw data, you can also decide to view it with a linear or log (base 10) y-axis. Note: if there are values equal to or less than 0 present, this will automatically cause the log10 y-axis to become infinite."), 
                    dcc.Dropdown(id = "plsda_any_metab_selection_UPLOADDATA", multi = True)
                ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Update selected metabolite plots", 
                                id = "btn-update-plsda-any-metab-sele_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    ])
                ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H5("Raw Data", style = {'textAlign':'center'}), 
                    html.P("Plot Type:"),
                    dcc.RadioItems(
                        id='plsda_raw_plot_type_sele_UPLOADDATA', 
                        options=['Bar Plot', 'Box Plot', 'Violin Plot'],
                        value='Bar Plot'
                        ),
                    html.Br(), 
                    html.P("Y-axis scale:"),
                    dcc.RadioItems(
                        id='plsda_raw_plot_yaxis_sele_UPLOADDATA', 
                        options=['Linear', 'Log10'],
                        value='Linear'
                        ),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "plsda_any_metab_raw_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    ], 
                    lg={"size":6}
                    ),
                dbc.Col([
                    html.H5("Normalised Data", style = {'textAlign':'center'}), 
                    html.P("Plot Type:"),
                    dcc.RadioItems(
                        id='plsda_norm_plot_type_sele_UPLOADDATA', 
                        options=['Bar Plot', 'Box Plot', 'Violin Plot'],
                        value='Bar Plot'
                        ),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(), #Added in to make graphs align in lg screen
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "plsda_any_metab_norm_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    ], 
                    lg={"size":6}
                    )
                ])
        ]
    ),
    className="mt-3",
)

volcano_tab = dbc.Card(
    dbc.CardBody(
        [
            html.Br(), 
            html.H4("Volcano plot", 
                    style={'textAlign': 'center'}),
            html.P("Select the samples group to compare against each other, where the selections in “Group 1” will be analysed against those in “Group 2”. Click “Update volcano plot” to view your results. The Fold-Change is calculated with the raw data and the p-value is calculated with the normalised data. Hover over a data point to see which metabolite it is and whether it is elevated in Group 1 or 2."),
            html.P("Images of your graphs and plots can be directly downloaded when you view them in their respective pages of this report. Simply hover your mouse cursor over your graph and select the camera icon to “Download plot as a png”."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H5("Group 1"), 
                    dcc.Dropdown(id="group-1-options_UPLOADDATA", multi=True)
                    ],
                    xs = {"size":12, "offset":0}, 
                    md = {"size":6, "offset":0}
                    ),
                dbc.Col([
                    html.H5("Group 2"), 
                    dcc.Dropdown(id="group-2-options_UPLOADDATA", multi=True)
                    ],
                    xs = {"size":12, "offset":0}, 
                    md = {"size":6, "offset":0}
                    )
                ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Update volcano plot", 
                                id = "btn-update-volcano-plot_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    ])
                ]), 
            html.P("To add a significance threshold to your volcano plot enter a numeric value in the text box provided. The p-value (-log10) for commonly used thresholds are provided in the table below:"), 
            dbc.Row([
                dbc.Col([
                    dash_table.DataTable(data = p_value_data.to_dict('records'), 
                                         columns=[{'id': c, 'name': c} for c in p_value_data.columns],
                                         style_cell = { 
                                             "font_family":"sans-serif"
                                             }
                                         ),
                    ], 
                    xs = 3, 
                    md = 2)
                ]),
            html.Br(),
            dcc.Input(id="volcano_sig_thres_UPLOADDATA", type="number", 
                      placeholder="Type numerical threshold"),
            dbc.Row([
                dbc.Spinner(
                    children=[
                        dcc.Graph(id = "volano-plot_UPLOADDATA")
                        ],
                    size = "lg", 
                    color = "primary", 
                    fullscreen = False
                    ),
                ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Download Volcano Plot Data", 
                                id = "btn-download-volcano-data_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    dcc.Download(id = "volano_data_to_download_UPLOADDATA"),
                    html.P("Downloaded data includes Volcano Plot values as well as the raw and normalised intensities of the metabolites across the samples."),
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":2}
                    ),
                ]),
            dbc.Row([
                html.H5("Examine metabolite", 
                        style={'textAlign': 'center'}),
                html.P("Select a metabolite data point from the volcano plot to see its average peak intensity across the sample groups (error bars indicate standard deviation)", 
                       style={'textAlign': 'center'}),
                ]),
            dbc.Row([
                dbc.Col([
                    html.H5("Raw data", style={'textAlign': 'center'}),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "volcano_metabolite_select_raw_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    ], 
                    lg={"size":6}
                    ),
                dbc.Col([
                    html.H5("Normalised data", style={'textAlign': 'center'}),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "volcano_metabolite_select_norm_UPLOADDATA")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    ], 
                    lg={"size":6}
                    ),
                ]),
        ]
    ),
    className="mt-3",
)

CustomHeatmap_tab = dbc.Card(
    dbc.CardBody(
        [
            html.Br(),
            html.H5("Custom Heatmaps", 
                    style={'textAlign': 'center'}),
            dcc.Markdown("Select which samples and metabolites you would like to present in your heatmap. Note: the colours in the heatmap are scaled by the average intensity for each **metabolite independently**. Therefore, this allows a comparison of intensities *within* rows but not *between* rows.", 
                   className="card-text"),
            dcc.Markdown("""For the best output, please select your desired sample group and metabolites **before** you select the "Update Heatmap" button.""", 
                   className="card-text"),
            html.P("Images of your graphs and plots can be directly downloaded when you view them in their respective pages of this report. Simply hover your mouse cursor over your graph and select the camera icon to “Download plot as a png”."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    ], 
                    xs = {"size":12, "offset":0}, 
                    md = {"size":6, "offset":0}
                    ), 
                dbc.Col([
                    dbc.Button(
                        'Select all metabolites', 
                        id = "customHeatmap_btn_allMetab_UPLOADDATA", 
                        n_clicks = 0
                        ),
                    dbc.Button(
                        'Clear all metabolites', 
                        id = "customHeatmap_btn_ClearMetab_UPLOADDATA", 
                        n_clicks = 0
                        ),
                    ])
                ]),
            dbc.Row([
                dbc.Col([
                    html.H5("Select Sample Groups"),
                    dcc.Dropdown(id = "customHeatmap_GroupSele_UPLOADDATA", 
                                 multi = True)
                    ], 
                    xs = {"size":12, "offset":0}, 
                    md = {"size":6, "offset":0}
                    ), 
                dbc.Col([
                    html.H5("Select Metabolites"), 
                    dcc.Dropdown(id = "customHeatmap_MetaboliteSele_UPLOADDATA", 
                                 multi = True)
                    ])
                ]), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Update Heatmap", 
                                id = "btn_update_customHeatmap_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    ])
                ]),
            html.Br(),
            dbc.Spinner(
                children=[
                    dcc.Graph(id = "customHeatmap_heatmap_UPLOADDATA")
                    ],
                size = "lg", 
                color = "primary", 
                fullscreen = False
                ),
        ]
    ),
    className="mt-3",
)

downloadData_tab = dbc.Card(
    dbc.CardBody(
        [
            html.Br(),
            dbc.Row((html.H2('Download Data', style={'textAlign': 'center'}) 
                              )),
            html.P("Use the buttons below or within the other tabs of your report to download your data as Excel Worksheet files. Note: Only the data you have currently selected for analyses will be included in the downloaded files."),
            html.P("Go to the Volcano Plot page to download this data."),
            html.P("Images of your graphs and plots can be directly downloaded when you view them in their respective pages of this report. Simply hover your mouse cursor over your graph and select the camera icon to “Download plot as a png”."),
            html.H5("Data Tables"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Raw data", 
                                id = "btn-download-raw-transposed_UPLOADDATA", 
                                className="mb-3",
                                color="primary"),
                    dcc.Download(id = "download-raw-transposed_UPLOADDATA")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":2}
                    ),
                dbc.Col([
                    dbc.Button("Normalised data", 
                                id = "btn-download-norm_UPLOADDATA", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-norm_UPLOADDATA")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":3, "offset":1}
                    ),
                ]),
            html.H5("PCA Data"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("PCA scores data", 
                                id = "btn-download-pca-scores_UPLOADDATA", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-pca-scores_UPLOADDATA")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":1}
                    ),
                dbc.Col([
                    dbc.Button("PCA loadings data", 
                                id = "btn-download-pca-loadings_UPLOADDATA", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-pca-loadings_UPLOADDATA")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":1}
                    ),
                dbc.Col([
                    dbc.Button("PCA VIP Scores", 
                                id = "btn-download-pca-vip-scores_UPLOADDATA", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-pca-vip-scores_UPLOADDATA")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":1}
                    ),
                ]),
            html.H5("PLS-DA Data"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("PLS-DA scores data", 
                                id = "btn-download-plsda-scores_UPLOADDATA", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-plsda-scores_UPLOADDATA")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":2}
                    ),
                dbc.Col([
                    dbc.Button("PLS-DA loadings data", 
                                id = "btn-download-plsda-loadings_UPLOADDATA", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-plsda-loadings_UPLOADDATA")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":2}
                    ),
                dbc.Col([
                    dbc.Button("PLS-DA VIP Scores", 
                                id = "btn-download-plsda-vip-scores_UPLOADDATA", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-plsda-vip-scores_UPLOADDATA")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":1}
                    ),
                ]), 
        ]
    ),
    className="mt-3",
)


layout = html.Div([
    dcc.Link("Go back to view other reports", href=accountIndexPage),
    html.Br(),
    html.H5("{}".format(page_name), style={'textAlign': 'center'}),
    #Save Data in the memory + allow to be shared between functions/tabs
    dbc.Spinner([
        dcc.Upload(
            id='upload-data_UPLOADDATA',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
                ]),
            style={'width': '100%', 'height': '60px', 'lineHeight': '60px',
                   'borderWidth': '1px', 'borderStyle': 'dashed',
                   'borderRadius': '5px','textAlign': 'center','margin': '10px'},
            # Only allow one file to be uploaded
            multiple=False
            ),
        html.Div(id='output-data-upload_UPLOADDATA'),
        ]),
    dbc.Spinner(
        children=[
            dcc.Store(id = "uploaded-store-data_UPLOADDATA", 
                      data = [], 
                      storage_type = "memory"),
            ],
        size = "lg", 
        color = "primary", 
        fullscreen = True
        ),
    dbc.Spinner(
        children=[
            dcc.Store(id = "store-data_UPLOADDATA", 
                      data = [], 
                      storage_type = "memory"),
            ],
        size = "lg", 
        color = "primary", 
        fullscreen = True
        ),
    dbc.Spinner(
        children=[
            dcc.Store(id = "store-raw-transposed-data_UPLOADDATA", 
                      data = [], 
                      storage_type = "memory"),
            ],
        size = "lg", 
        color = "primary", 
        fullscreen = True
        ),
    html.Br(),
    dbc.Row([
        html.H3("Remove samples by group and/or individually", 
                style={'textAlign': 'center'}),
        html.P(dcc.Markdown("""
        - Click the dropdown buttons below to remove and select either groups or individual samples to include in downstream analyses. 
        - Please allow the form to update between selections
        - **Note**: the individual and group sample lists do not refresh relative to each other, but the data will be subset according to which items you remove. Check the data tables in the “Raw data” or “Normalised data” pages to see which samples are present in your selected data. 
        - You can refresh the webpage to reset your choices
        - Click the “Update form with data selection” button to view your results
                            """), 
               )
        ]), 
    dbc.Row([
        dbc.Col([
            dbc.Button(
                'Click here to select sample groups',
                id="btn_group_collapse_0_UPLOADDATA", 
                #color = "info",
                n_clicks = 0
                ), 
            dbc.Collapse(
                dcc.Dropdown(
                    id = "label_selection_UPLOADDATA",
                    #options = label_list, 
                    # value = label_list, 
                    multi = True, 
                    #style = {"overflow-y":"scroll", "height": "280px"}
                    ), 
                id="group_list_collapse_UPLOADDATA", 
                is_open=False
                )
            ], 
            xs = {"size":12, "offset":0},
            md = {"size":6, "offset":0}), 
        dbc.Col([
            dbc.Button(
                'Click here to select individual samples', 
                id="btn_individual_collapse_0_UPLOADDATA", 
                #color = "info",
                n_clicks = 0
                ), 
            dbc.Collapse(
                dcc.Dropdown(
                    id = "sample_selection_UPLOADDATA",
                    #options = sample_list, 
                    # value = sample_list, 
                    multi = True, 
                    #style = {"overflow-y":"scroll", "height": "280px"}
                    ), 
                id="individual_list_collapse_UPLOADDATA", 
                is_open=False
                )
            ], 
            xs = {"size":12, "offset":0},
            md = {"size":6, "offset":0})
        ]), 
    #Button to update data
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Button("Update form with data selection", 
                        id = "btn-update-form_data0_UPLOADDATA", 
                        className="mb-3",
                        color="success"),
            ]),
        ]),
    html.Br(), 
    dbc.Tabs(
    [
        dbc.Tab(PCA_tab, label="PCA Results"),
        dbc.Tab(PLSDA_tab, label="PLSDA Results"),
        dbc.Tab(volcano_tab, label="Volcano Plot"),
        dbc.Tab(CustomHeatmap_tab, label = "Custom Heatmap"),
        dbc.Tab(rawData_tab, label="Raw data"),
        dbc.Tab(normData_tab, label="Normalised data"),
        dbc.Tab(downloadData_tab, label = "Download Data")
    ])
    ])

#Allow Tessa to upload data in a CSV file
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    # decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            pass
            # df = pd.read_csv(
            #     io.StringIO(decoded.decode('utf-8')), delimiter=";")
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file. Please upload a CSV file in the correct MetaboAnalyst-ready format'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

#Output file only (to be saved in the memory for data selection)
def parse_contents_toSave(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8'))#, delimiter=";"
                )
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file. Please upload a CSV file in the correct MetaboAnalyst-ready format'
        ])

    return df.to_json(date_format='iso', orient = 'split')

@callback([Output('output-data-upload_UPLOADDATA', 'children'),
          Output('uploaded-store-data_UPLOADDATA', "data"), 
          Output('label_selection_UPLOADDATA', 'options'),
          Output('sample_selection_UPLOADDATA', 'options'),
          Output('label_selection_UPLOADDATA', 'value'),
          Output('sample_selection_UPLOADDATA', 'value'),
          Input('upload-data_UPLOADDATA', 'contents'),
          State('upload-data_UPLOADDATA', 'filename'),
          State('upload-data_UPLOADDATA', 'last_modified')
          ], 
          prevent_initial_call = True)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is None:
        raise PreventUpdate
    else:
        if list_of_contents is not None:
            children = [parse_contents(list_of_contents, list_of_names, list_of_dates)]
            df = pd.read_json(parse_contents_toSave(list_of_contents, list_of_names, list_of_dates), orient = 'split')
            
            df_sel = pd.DataFrame(df)
            
            #Transpose the data --> in "tidy data" format, with samples as rows
            df_sel = df_sel.set_index(df_sel.columns[0]).transpose()
            #Make a numerical index
            df_sel = df_sel.rename_axis("Sample").reset_index()
            #Remove the name of the numerical index
            df_sel = df_sel.rename_axis(None, axis = 1)
            #Convert all variables containing numbers to numeric-type variables
            df_sel = df_sel.apply(pd.to_numeric, 
                          errors = "ignore"
                          )
            df_sel = df_sel.replace(to_replace = 0, value = 0.001)
            
            #Create options to select by label and individual samples for the uploaded data
            #Create a label list
            label_list = list(df_sel["Label"].unique())
            #Create a sample list
            sample_list = list(df_sel["Sample"])
            
            return children, df.to_dict("records"), label_list, sample_list, label_list, sample_list

#Display Sample groups to select when button clicked
@callback(
    Output("group_list_collapse_UPLOADDATA", "is_open"), 
    Input("btn_group_collapse_0_UPLOADDATA", "n_clicks"), 
    State("group_list_collapse_UPLOADDATA", "is_open")
    )
def toggle_group_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

#Display individual samples to select when button clicked
@callback(
    Output("individual_list_collapse_UPLOADDATA", "is_open"), 
    Input("btn_individual_collapse_0_UPLOADDATA", "n_clicks"), 
    State("individual_list_collapse_UPLOADDATA", "is_open")
    )
def toggle_individual_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

#Subset data frame + save in memory storage
@callback(
    [Output('store-data_UPLOADDATA', "data"),
     Output('store-raw-transposed-data_UPLOADDATA', "data"),
     Output('pca_any_metab_selection_UPLOADDATA', 'options'),
     Output('plsda_any_metab_selection_UPLOADDATA', 'options')
     ],
    [Input("btn-update-form_data0_UPLOADDATA", "n_clicks"),
     Input("uploaded-store-data_UPLOADDATA", "data"),
     Input("label_selection_UPLOADDATA", "value"),
     Input("sample_selection_UPLOADDATA", "value")], 
    prevent_initial_call=True
    )
 
def update_data(n_clicks, df_sel, value_label, value_sample):
    
    if n_clicks is None:
        raise PreventUpdate
    #Only update data once user has selected it
    else:
        #Read raw metabolomics data
        # df_sel = pd.read_csv('ProsperityExperiment2_Expt 2 Untargeted annotated Cell Pellet BC For MetaboAnalyst.csv')
        # print("df_sel directly from directory")
        # print(df_sel.columns)

        df_sel = pd.DataFrame(df_sel)
        
        #Transpose the data --> in "tidy data" format, with samples as rows
        df_sel = df_sel.set_index(df_sel.columns[0]).transpose()
        #Make a numerical index
        df_sel = df_sel.rename_axis("Sample").reset_index()
        #Remove the name of the numerical index
        df_sel = df_sel.rename_axis(None, axis = 1)
        #Convert all variables containing numbers to numeric-type variables
        df_sel = df_sel.apply(pd.to_numeric, 
                      errors = "ignore"
                      )
        df_sel = df_sel.replace(to_replace = 0, value = 0.001)
        #Put table into alphabetical order by Sample
        #df_sel.sort_values("Sample", ascending=False)
        
        #df_sel = df.copy()
        
        #Only keep selected Samples/Labels
        df_sel = df_sel[df_sel['Label'].isin(list(value_label))]
        df_sel = df_sel[df_sel['Sample'].isin(list(value_sample))]
        
        df_raw_transposed = df_sel.copy()
        #Filtering Dataframe rows in the non-normalised data
        #Therefore: both have the same selected user data 
        #nonlocal df_raw_transposed
        df_raw_transposed = df_raw_transposed[df_raw_transposed.Sample.isin(df_sel.Sample)]
        
        #sample_list = list(df_sel["Sample"])
        
        ## Log transformation + mean-centre and Pareto scaling
        #Log transform numeric columns
        df_sel = df_sel.apply(lambda x: np.log10(x) if np.issubdtype(x.dtype, np.number) else x)
        
        #Mean-centre scaling
        df_sel = df_sel.apply(lambda x: x-x.mean() if np.issubdtype(x.dtype, np.number) else x)
        
        #Pareto scaling
        df_sel = df_sel.apply(lambda x: x/math.sqrt(x.std()) if np.issubdtype(x.dtype, np.number) else x)
        
        #Remove metabolites where NaNs are introduced 
        #E.g. when Sample subsetting makes STDEV = 0 --> get divide by 0 error
        df_sel = df_sel.dropna(axis=1)
        
        #Round the numerical values to 6 decimal places
        df_sel = df_sel.apply(lambda x: round(x, 6) if np.issubdtype(x.dtype, np.number) else x)
        
        #Put table into alphabetical order by Sample
        df_sel.sort_values("Sample", ascending=False)
        
        #Get list of metabolites for metabolite selection (PCA and PLSDA pages)
        str_variables = set(df_sel.select_dtypes("object" or "str").columns)
        #Remove the str_variables to get metabolites only
        pca_metabolite_list = [metabolite for metabolite in 
                           list(df_sel.columns) if metabolite not in list(str_variables)]
        plsda_metabolite_list = pca_metabolite_list

    #Return data as a list of dictionaries
    return df_sel.to_dict("records"), df_raw_transposed.to_dict("records"), pca_metabolite_list, plsda_metabolite_list

#Display raw data table
@callback(
    [Output("display_subset_raw_tabs_UPLOADDATA", "children"), 
     Output("histrogram_raw_UPLOADDATA", "figure")
     ],
    Input("store-raw-transposed-data_UPLOADDATA", "data"),
    prevent_initial_call = True
    )
def update_raw_table_scriptInitiate(data):
    
    overview_table, hist_raw = ReportFunctions.update_raw_table(data)
    
    return overview_table, hist_raw

#Display normalised data table
@callback(
    [Output('display_subset_tabs_UPLOADDATA', "children"),
     Output("histogram_norm_UPLOADDATA", "figure")
     ],
    Input("store-data_UPLOADDATA", "data"),
    prevent_initial_call = True
    )
def update_normalised_table_scriptInitiate(data):
    
    overview_table, hist_norm = ReportFunctions.update_normalised_table(data)
    
    return overview_table, hist_norm

#Interactive PCA plots
@callback(
    [Output("pca_scores_plot_UPLOADDATA", "figure"),
    Output("pca_loadings_plot_UPLOADDATA", "figure"),
    Output("pca_vip_plot_UPLOADDATA", "figure"), 
    Output("pca_group_avg_heatmap_UPLOADDATA", "figure")
    ],
    [Input("store-data_UPLOADDATA", "data")],
    prevent_initial_call = True
)
def update_pca_scriptInitialise(data):
    
    pca_scores_plot, pca_loadings_plot, vip_plot_pca, heatmap_mean_pca = ReportFunctions.update_pca_UserGroupOrder(data)
    
    return pca_scores_plot, pca_loadings_plot, vip_plot_pca, heatmap_mean_pca

#Select metabolite from loadings plot
@callback(
    Output('pca_metabolite_select_raw_UPLOADDATA', 'figure'),
     Output("pca_metabolite_select_norm_UPLOADDATA", "figure"),
    [Input('pca_loadings_plot_UPLOADDATA', 'clickData'),
     Input("store-raw-transposed-data_UPLOADDATA", "data"), 
     Input("store-data_UPLOADDATA", "data")
     ], prevent_initial_call = True
    )
def update_average_plots_pca_scriptInitialise(clickData, df_raw_T, df_norm):
    
    fig_raw_pca, fig_norm_pca = ReportFunctions.update_average_plots_pca(clickData, df_raw_T, df_norm)
    
    return fig_raw_pca, fig_norm_pca

#Update metabolite selection plots (PCA)
@callback(
    Output('pca_any_metab_raw_UPLOADDATA', 'figure'), 
    Output('pca_any_metab_norm_UPLOADDATA', 'figure'), 
    Output('pca_any_metab_eachSample_raw_UPLOADDATA', 'figure'),
    Input('btn-update-pca-any-metab-sele_UPLOADDATA', 'n_clicks'),
    Input('store-raw-transposed-data_UPLOADDATA', 'data'), 
    Input('store-data_UPLOADDATA', 'data'), 
    Input('pca_raw_plot_type_sele_UPLOADDATA', 'value'),
    Input('pca_raw_plot_yaxis_sele_UPLOADDATA', 'value'),
    Input('pca_norm_plot_type_sele_UPLOADDATA', 'value'),
    State('pca_any_metab_selection_UPLOADDATA', 'value'), 
    prevent_initial_call = True
)

def pca_any_metab_plots(n_clicks, data_raw, data_norm, rawplot_type, rawplot_axis, normplot_type, metabolite_name):
    if n_clicks is None:
        raise PreventUpdate
    else:
        metabolite_name = list(metabolite_name)
        
        data_raw = pd.DataFrame(data_raw)
        data_norm = pd.DataFrame(data_norm)

        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        str_variables = set(data_raw.select_dtypes("object" or "str").columns)
        
        #Create list of columns names with str_variables + metabolite of interest
        columns_keep = str_variables
        columns_keep = columns_keep.union(metabolite_name)
        
        ## Average bar plots (raw data)
        #Create new df subset with data in columns_keep
        df_average_pre = data_raw[list(columns_keep)]
        #Convert to long data format
        df_average_pre = pd.melt(df_average_pre, 
                                 id_vars = ['Label', 'Sample'],
                                 var_name='Metabolites',
                                 value_name='Intensities',
                                 value_vars=list(metabolite_name))
        #Keep copy of data with the sample column
        df_all_samples_raw = df_average_pre.copy()
        #Remove sample column for data to be averaged (groupby function does not like it being present)
        df_average_pre = df_average_pre.drop('Sample', axis=1)
        
        #Calculate the average and standard deviations by Label group 
        df_average = pd.DataFrame(df_average_pre.groupby(["Label", "Metabolites"]).mean()).reset_index()
        df_average = df_average.rename(columns = {"Intensities":"Mean"})
        
        label_order = list(df_average["Label"].unique())
        
        df_stdev = pd.DataFrame(df_average_pre.groupby(["Label", "Metabolites"]).std()).reset_index()
        df_stdev = df_stdev.rename(columns = {"Intensities":"STDEV"})
        
        #Merge the average and stdev results 
        df_graph = pd.concat([df_average, df_stdev["STDEV"]], axis = 1)
        
        ## Average bar plots (normalised data)
        #Create new df subset with data in columns_keep
        df_average_pre_norm = data_norm[list(columns_keep)]
        #Convert to long data format
        df_average_pre_norm = pd.melt(df_average_pre_norm, 
                                 id_vars = 'Label',
                                 var_name='Metabolites',
                                 value_name='Intensities',
                                 value_vars=list(metabolite_name))
        
        #Calculate the average and standard deviations by Label group 
        df_average_norm = pd.DataFrame(df_average_pre_norm.groupby(["Label", "Metabolites"]).mean()).reset_index()
        df_average_norm = df_average_norm.rename(columns = {"Intensities":"Mean"})
        
        #label_order_norm = list(df_average_norm["Label"].unique())
        
        df_stdev_norm = pd.DataFrame(df_average_pre_norm.groupby(["Label", "Metabolites"]).std()).reset_index()
        df_stdev_norm = df_stdev_norm.rename(columns = {"Intensities":"STDEV"})
        
        #Merge the average and stdev results 
        df_graph_norm = pd.concat([df_average_norm, df_stdev_norm["STDEV"]], axis = 1)
        
        #If user selects Bar Plot for Raw data
        if rawplot_type == "Bar Plot":
            
            #If user selects Linear Y-axis
            if rawplot_axis == "Linear":
                pca_any_metab_raw_fig = go.Figure()
                for metabolite in list(metabolite_name):
                    pca_any_metab_raw_fig.add_trace(go.Bar(name=metabolite,
                                         x=df_graph['Label'].unique(),
                                         y=df_graph['Mean'][df_graph['Metabolites'] == metabolite],
                                         error_y=dict(type='data',
                                                      array=df_graph['STDEV'][df_graph['Metabolites'] == metabolite])))
                
                pca_any_metab_raw_fig.update_layout(barmode='group', 
                                                    yaxis_title="Raw Intensities")
                pca_any_metab_raw_fig.update_xaxes(categoryorder='array', 
                                                   categoryarray=label_order)
                
            #If user selects Log10 Y-axis
            else:
                pca_any_metab_raw_fig = go.Figure()
                for metabolite in list(metabolite_name):
                    pca_any_metab_raw_fig.add_trace(go.Bar(name=metabolite,
                                         x=df_graph['Label'].unique(),
                                         y=df_graph['Mean'][df_graph['Metabolites'] == metabolite],
                                         error_y=dict(type='data',
                                                      array=df_graph['STDEV'][df_graph['Metabolites'] == metabolite])))
                
                pca_any_metab_raw_fig.update_layout(barmode='group', 
                                                    yaxis_title="Raw Intensities (log10)")
                pca_any_metab_raw_fig.update_yaxes(type="log")
        
        #If user selects Box plot for Raw data
        elif rawplot_type == "Box Plot":
            #Create new df subset with data in columns_keep
            df_box = data_raw[list(columns_keep)]
            #Convert to long data format
            df_box = pd.melt(df_box, 
                             id_vars = 'Label',
                             var_name='Metabolites',
                             value_name='Intensities',
                             value_vars=list(metabolite_name))
            
            #If user selects Linear Y-axis
            if rawplot_axis == 'Linear':
                pca_any_metab_raw_fig = px.box(df_box, 
                                x = 'Label', 
                                y = 'Intensities', 
                                color = 'Metabolites', 
                                category_orders = {'Metabolites':list(metabolite_name), 
                                                   'Label':sorted(list(df_box["Label"].unique()))}, 
                                labels={"Intensities": "Raw Intensities"},
                                )
            else:
                pca_any_metab_raw_fig = px.box(df_box, 
                                x = 'Label', 
                                y = 'Intensities', 
                                color = 'Metabolites', 
                                category_orders = {'Metabolites':list(metabolite_name), 
                                                   'Label':sorted(list(df_box["Label"].unique()))},
                                labels={"Intensities": "Raw Intensities (log10)"},
                                log_y = True
                                )    
                
        #If user selects violin plot for Raw data
        elif rawplot_type == "Violin Plot": 
            df_violin = data_raw[list(columns_keep)]
            #Convert to long data format
            df_violin = pd.melt(df_violin, 
                             id_vars = 'Label',
                             var_name='Metabolites',
                             value_name='Intensities',
                             value_vars=list(metabolite_name))
            pca_any_metab_raw_fig = go.Figure
            
            #If user selects Linear Y-axis
            if rawplot_axis == 'Linear':
                pca_any_metab_raw_fig = px.violin(df_violin, 
                                x = 'Label', 
                                y = 'Intensities', 
                                color = 'Metabolites', 
                                category_orders = {'Metabolites':list(metabolite_name), 
                                                    'Label':sorted(list(df_violin["Label"].unique()))}, 
                                labels={"Intensities": "Raw Intensities"},
                                )
            else:
                pca_any_metab_raw_fig = px.violin(df_violin, 
                                x = 'Label', 
                                y = 'Intensities', 
                                color = 'Metabolites',
                                category_orders = {'Metabolites':list(metabolite_name), 
                                                   'Label':sorted(list(df_violin["Label"].unique()))},
                                labels={"Intensities": "Raw Intensities (log10)"},
                                log_y = True
                                ) 
            
        
        #If user selects Bar Plot for Normalised data
        if normplot_type == "Bar Plot":
            
            pca_any_metab_norm_fig = go.Figure()
            for metabolite in list(metabolite_name):
                pca_any_metab_norm_fig.add_trace(go.Bar(name=metabolite,
                                     x=df_graph_norm['Label'].unique(),
                                     y=df_graph_norm['Mean'][df_graph_norm['Metabolites'] == metabolite],
                                     error_y=dict(type='data',
                                                  array=df_graph_norm['STDEV'][df_graph_norm['Metabolites'] == metabolite])))
            
            pca_any_metab_norm_fig.update_layout(barmode='group', 
                                                 yaxis_title="Normalised Intensities")
                
        #If user selects Box Plot for normalised data    
        elif normplot_type == "Box Plot":
            #Create new df subset with data in columns_keep
            df_box_norm = data_norm[list(columns_keep)]
            #Convert to long data format
            df_box_norm = pd.melt(df_box_norm, 
                             id_vars = 'Label',
                             var_name='Metabolites',
                             value_name='Intensities',
                             value_vars=list(metabolite_name))
            pca_any_metab_norm_fig = px.box(df_box_norm, 
                            x = 'Label', 
                            y = 'Intensities', 
                            color = 'Metabolites', 
                            category_orders = {'Metabolites':list(metabolite_name),
                                               'Label':sorted(list(df_box_norm["Label"].unique()))}, 
                            labels={"Intensities": "Normalised Intensities"},
                            )
        
        elif normplot_type == "Violin Plot":
            #Create new df subset with data in columns_keep
            df_violin_norm = data_norm[list(columns_keep)]
            #Convert to long data format
            df_violin_norm = pd.melt(df_violin_norm, 
                             id_vars = 'Label',
                             var_name='Metabolites',
                             value_name='Intensities',
                             value_vars=list(metabolite_name))
            pca_any_metab_norm_fig = px.violin(df_violin_norm, 
                            x = 'Label', 
                            y = 'Intensities', 
                            color = 'Metabolites', 
                            category_orders = {'Metabolites':list(metabolite_name),
                                               'Label':sorted(list(df_violin_norm["Label"].unique()))}, 
                            labels={"Intensities": "Normalised Intensities"},
                            )
            
        #Plot bar plot for individual samples
        total_colours = px.colors.DEFAULT_PLOTLY_COLORS + px.colors.DEFAULT_PLOTLY_COLORS + px.colors.DEFAULT_PLOTLY_COLORS
        total_colours = total_colours[0:len(df_all_samples_raw["Metabolites"].unique())]
        dict_GroupColours = {'Metabolites':df_all_samples_raw["Metabolites"].unique(), 
                'colour':total_colours}
        GroupColours = pd.DataFrame(dict_GroupColours)
        
        # df_all_samples_average = df_all_samples_raw.copy()
        df_all_samples_average = df_all_samples_raw.drop('Label', axis=1)
        df_all_samples_average['Intensities'] = df_all_samples_average['Intensities'].astype(float)
        df_all_samples_average = df_all_samples_average.groupby('Metabolites').mean(numeric_only =True)
        df_all_samples_average = df_all_samples_average.reset_index(drop=False, inplace=False)
        df_all_samples_average['Intensities'] = df_all_samples_average['Intensities'].astype(float)
        df_all_samples_average = df_all_samples_average.rename(columns={'Intensities':'AverageIntensities'})
        # df_all_samples_average = pd.DataFrame(df_all_samples_average)
        #Keep metabolites in the correct order (based on user selection)
        df_all_samples_average = df_all_samples_average.set_index('Metabolites')
        df_all_samples_average = df_all_samples_average.reindex(metabolite_name, axis=0)
        df_all_samples_average = df_all_samples_average.reset_index(drop=False, inplace=False)
        
        if rawplot_axis == 'Linear':
            pca_any_metab_AllSamps_raw_fig = px.bar(df_all_samples_raw, x="Sample", 
                                           y="Intensities",
                                           color="Metabolites",
                                           labels={"Intensities": "Raw Intensities"},
                                           barmode="group")
            for index, row in GroupColours.iterrows():
                # print(row[0])
                # print(row[1])
                subset = df_all_samples_average.loc[df_all_samples_average['Metabolites'] == row[0]]
                averageIntensity = subset.at[index, 'AverageIntensities']
                # print("averageIntensity:", averageIntensity)
                pca_any_metab_AllSamps_raw_fig.add_hline(
                    y=averageIntensity, 
                    line_width=3, 
                    line_dash="dash",
                    line_color=row[1])
        else:
            pca_any_metab_AllSamps_raw_fig = px.bar(df_all_samples_raw, x="Sample", 
                                           y="Intensities",
                                           color="Metabolites", 
                                           barmode="group", 
                                           labels={"Intensities": "Raw Intensities (log10)"},
                                           log_y = True)
            for index, row in GroupColours.iterrows():
                # print(row[0])
                # print(row[1])
                subset = df_all_samples_average.loc[df_all_samples_average['Metabolites'] == row[0]]
                averageIntensity = subset.at[index, 'AverageIntensities']
                # print("averageIntensity:", averageIntensity)
                pca_any_metab_AllSamps_raw_fig.add_hline(
                    y=averageIntensity, 
                    line_width=3, 
                    line_dash="dash",
                    line_color=row[1])
            
        del [n_clicks, metabolite_name, data_raw, data_norm, str_variables, 
             columns_keep, rawplot_type, df_stdev, df_average, 
             label_order, df_graph, rawplot_axis, normplot_type]
        
    return pca_any_metab_raw_fig, pca_any_metab_norm_fig, pca_any_metab_AllSamps_raw_fig

#Interactive PLS-DA plots
@callback(
    [Output("interactive_plsda_plot_2D_UPLOADDATA", "figure"), 
    Output("plsda_loadings_plot_UPLOADDATA", "figure"), 
    Output("plsda_vip_plot_UPLOADDATA", "figure"), 
    Output("plsda_group_avg_heatmap_UPLOADDATA", "figure")
    ],
    [Input("store-data_UPLOADDATA", "data")],
    prevent_initial_call = True
    #State('interactive_pca_plot_2D', "figure")
)
def update_plsda_scriptInitialise(data):
    
    interactive_plsda_plot_2D, plsda_loadings_plot, vip_plot_plsda, heatmap_mean_plsda = ReportFunctions.update_plsda(data)
    
    return interactive_plsda_plot_2D, plsda_loadings_plot, vip_plot_plsda, heatmap_mean_plsda

#Select metabolite from loadings plot
@callback(
    Output('plsda_metabolite_select_raw_UPLOADDATA', 'figure'),
     Output("plsda_metabolite_select_norm_UPLOADDATA", "figure"),
    [Input('plsda_loadings_plot_UPLOADDATA', 'clickData'),
     Input("store-raw-transposed-data_UPLOADDATA", "data"), 
     Input("store-data_UPLOADDATA", "data")
     ], prevent_initial_call = True
    )
def update_average_plots_plsda_scriptInitialise(clickData, df_raw_T, df_norm):
    
    fig_raw_plsda, fig_norm_plsda = ReportFunctions.update_average_plots_plsda(clickData, df_raw_T, df_norm)
    
    return fig_raw_plsda, fig_norm_plsda

#Update metabolite selection plots (PLSDA)
@callback(
    Output('plsda_any_metab_raw_UPLOADDATA', 'figure'), 
    Output('plsda_any_metab_norm_UPLOADDATA', 'figure'), 
    Input('btn-update-plsda-any-metab-sele_UPLOADDATA', 'n_clicks'),
    Input('store-raw-transposed-data_UPLOADDATA', 'data'), 
    Input('store-data_UPLOADDATA', 'data'), 
    Input('plsda_raw_plot_type_sele_UPLOADDATA', 'value'),
    Input('plsda_raw_plot_yaxis_sele_UPLOADDATA', 'value'),
    Input('plsda_norm_plot_type_sele_UPLOADDATA', 'value'),
    State('plsda_any_metab_selection_UPLOADDATA', 'value'), 
    prevent_initial_call = True
)
def plsda_any_metab_plots_scriptInitialise(n_clicks, data_raw, data_norm, rawplot_type, rawplot_axis, normplot_type, metabolite_name):
    
    plsda_any_metab_raw_fig, plsda_any_metab_norm_fig = ReportFunctions.plsda_any_metab_plots(n_clicks, 
                                                                              data_raw, data_norm, rawplot_type, 
                                                                              rawplot_axis, normplot_type, 
                                                                              metabolite_name)
    
    return plsda_any_metab_raw_fig, plsda_any_metab_norm_fig

#Create selection lists from data in memory (for volcano plot)
@callback(
    Output("group-1-options_UPLOADDATA", "options"),
    Output("group-2-options_UPLOADDATA", "options"),
    Input("store-raw-transposed-data_UPLOADDATA", "data"),
    prevent_initial_call = True
)
def group_options(data):
    if data is None:
        raise PreventUpdate
    else:
        df = pd.DataFrame(data)
        
        #Remove QCs, blanks, and standards from Volcano Plot selection
        #TODO: Need to update for each dataset
        to_remove = ['Blank', 'QC Pool']
        
        options_group1 = list(df["Label"].unique())
        options_group2 = list(df["Label"].unique())
        
        #Delete removable items only if they are present in the overall user-selected data
        for element in to_remove:
            if element in options_group1:
                #Remove element from list
                options_group1.remove(element)
            else:
                pass
            
        for element in to_remove:
            if element in options_group2:
                #Remove element from list
                options_group2.remove(element)
            else:
                pass
    
        #Delete intermediate object (save memory space)
        del [df, to_remove]

    return options_group1, options_group2

#Make Volcano plot
@callback(
    Output("volano-plot_UPLOADDATA", "figure"),
    Input("btn-update-volcano-plot_UPLOADDATA", "n_clicks"),
    Input("store-raw-transposed-data_UPLOADDATA", "data"),
    State("group-1-options_UPLOADDATA", "value"),
    State("group-2-options_UPLOADDATA", "value"), 
    Input("volcano_sig_thres_UPLOADDATA", "value"),
    prevent_initial_call = True
)
def volcanic_eruption_scriptInitialise(n_clicks, data, state_1, state_2, sig_thres):
    
    volcano_plot = ReportFunctions.volcanic_eruption(n_clicks, data, state_1, state_2, sig_thres)
    
    return volcano_plot

#Create selection lists from data in memory (for custom Heatmap)
@callback(
    Output("customHeatmap_GroupSele_UPLOADDATA", "options"),
    Output("customHeatmap_MetaboliteSele_UPLOADDATA", "options"),
    Output("customHeatmap_MetaboliteSele_UPLOADDATA", "value"),
    Input("store-data_UPLOADDATA", "data"),
    Input("customHeatmap_btn_allMetab_UPLOADDATA", "n_clicks"),
    Input("customHeatmap_btn_ClearMetab_UPLOADDATA", "n_clicks"), 
    prevent_initial_call = True
)
def heatmap_options(data, allMetabolites, clearMetabolites):
    if data is None:
        raise PreventUpdate
    else:
        
        df = pd.DataFrame(data)
              
        SampleSele = list(df["Label"].unique())
        
        str_variables = set(df.select_dtypes("object" or "str").columns)
        
        #Remove the str_variables to get metabolites only
        MetaboliteSele = [metabolite for metabolite in 
                           list(df.columns) if metabolite not in list(str_variables)]
        
        #Delete intermediate object (save memory space)
        del [df, str_variables]
        
        #If all metabolites are selected: update the value of the dropdown
        if "customHeatmap_btn_allMetab_UPLOADDATA" == ctx.triggered_id:
            
            value_MetaboliteSele = MetaboliteSele.copy()
            
            return SampleSele, MetaboliteSele, value_MetaboliteSele
        
        #If not all metabolites are selected: make the dropdown value nothing
        elif "customHeatmap_btn_ClearMetab_UPLOADDATA" == ctx.triggered_id:
            
            value_MetaboliteSele = []
            
            return SampleSele, MetaboliteSele, value_MetaboliteSele
        
        # else:
        elif "customHeatmap_btn_ClearMetab_UPLOADDATA" != ctx.triggered_id or "customHeatmap_btn_allMetab_UPLOADDATA" != ctx.triggered_id:
            
            value_MetaboliteSele = []
            
            return SampleSele, MetaboliteSele, value_MetaboliteSele

#Create custom heatmaps
@callback(
    Output("customHeatmap_heatmap_UPLOADDATA", "figure"),
     Input("btn_update_customHeatmap_UPLOADDATA", "n_clicks"),
     State("store-data_UPLOADDATA", "data"), 
     State("customHeatmap_GroupSele_UPLOADDATA", "value"), 
     State("customHeatmap_MetaboliteSele_UPLOADDATA", "value"), 
     prevent_initial_call = True
)
def CustomHeatmap_scriptInitialise(n_clicks, data, SelectedGroups, SelectedMetabolites):
    
    custom_heatmap = ReportFunctions.CustomHeatmap(n_clicks, data, SelectedGroups, SelectedMetabolites)
    
    return custom_heatmap

#Download volcano plot data
@callback(
    Output("volano_data_to_download_UPLOADDATA", "data"),
    Input("btn-download-volcano-data_UPLOADDATA", "n_clicks"),
    Input("store-raw-transposed-data_UPLOADDATA", "data"),
    State("group-1-options_UPLOADDATA", "value"),
    State("group-2-options_UPLOADDATA", "value"), 
    Input("volcano_sig_thres_UPLOADDATA", "value"),
    Input("store-data_UPLOADDATA", "data"), 
    prevent_initial_call = True
)
def volcanic_eruption_download_scriptInitialise(n_clicks, data_raw, state_1, state_2, sig_thres, data_norm):
    
    #Function creates the file to be 'sent' to the user to download in the return function below
    ReportFunctions.volcanic_eruption_download(n_clicks, data_raw, state_1, state_2, sig_thres, data_norm, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_Volcano_plot_data.xlsx")

#Select metabolite from volcano plot
@callback(
    Output('volcano_metabolite_select_raw_UPLOADDATA', 'figure'),
     Output("volcano_metabolite_select_norm_UPLOADDATA", "figure"),
    [Input('volano-plot_UPLOADDATA', 'clickData'),
     Input("store-raw-transposed-data_UPLOADDATA", "data"), 
     Input("store-data_UPLOADDATA", "data")
     ], prevent_initial_call = True
    )
def update_average_plots_volcano_scriptInitialise(clickData, df_raw_T, df_norm):
    
    fig_raw_volcano, fig_norm_volcano = ReportFunctions.update_average_plots_volcano(clickData, df_raw_T, df_norm)
    
    return fig_raw_volcano, fig_norm_volcano

#Make Batch Correction PCA plot
@callback(
    Output("intracellular-non-batchCorrection-pca_plot_UPLOADDATA", "figure"),
    Output("intracellular-batchCorrection-pca_plot_UPLOADDATA", "figure"),
    Output("extracellular-non-batchCorrection-pca_plot_UPLOADDATA", "figure"),
    Output("extracellular-batchCorrection-pca_plot_UPLOADDATA", "figure"),
    Input("btn-update-batchCorrection_UPLOADDATA", "n_clicks"), 
    prevent_initial_call = True
)
def batch_correction_visualisation(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else: #Only update the if batch correction plot button is clicked
        #Tasks to do manually beforehand
        # 1) Create BatchLabelAssignments.csv
        # 2) Remove extra rows and columns from the pre-Batch Corrected datasets
        # 3) Get PCA scores data (grouped by Batch) from MetaboAnalyst
        
        #Load in the data
        initial_intra = pd.read_csv("ProsperityExperiment2_BatchCorrectionPCAData_CellPellet_PreBatchCorrected.csv", 
                                    skipinitialspace = True)
        initial_extra = pd.read_csv("ProsperityExperiment2_BatchCorrectionPCAData_SpentMedia_PreBatchCorrected.csv", 
                                    skipinitialspace = True)
        final_intra = pd.read_csv("ProsperityExperiment2_BatchCorrectionPCAData_CellPellet_BatchCorrected.csv", 
                                  skipinitialspace = True)
        final_extra = pd.read_csv("ProsperityExperiment2_BatchCorrectionPCAData_SpentMedia_BatchCorrected.csv", 
                                  skipinitialspace = True)
        
        #Load in Sample Name:Batch assignments
        batch_label_intra = pd.read_csv("ProsperityExperiment2_BatchSampleAssignments_CellPellet.csv", 
                                        skipinitialspace = True)
        batch_label_extra = pd.read_csv("ProsperityExperiment2_BatchSampleAssignments_SpentMedia.csv", 
                                        skipinitialspace = True)
        
        #Specify % variance on each axis (from MetaboAnalyst)
        initial_intra_Var_PC1 = 13.6
        initial_intra_Var_PC2 = 8.3
        final_intra_Var_PC1 = 12.6
        final_intra_Var_PC2 = 9.8
        
        initial_extra_Var_PC1 = 16
        initial_extra_Var_PC2 = 9.7
        final_extra_Var_PC1 = 14.3
        final_extra_Var_PC2 = 7.5
        
        #Tidy Name:Batch assignment data
        batch_label_intra = batch_label_intra.applymap(lambda x: str(x).rstrip(' R'))
        batch_label_intra = batch_label_intra.applymap(lambda x: str(x).rstrip(' RR'))
        batch_label_intra = batch_label_intra.applymap(lambda x: str(x).rstrip(' '))
        batch_label_intra['Name'] = batch_label_intra['Name'].str.replace(' ', '_')
        
        batch_label_extra = batch_label_extra.applymap(lambda x: str(x).rstrip(' R'))
        batch_label_extra = batch_label_extra.applymap(lambda x: str(x).rstrip(' RR'))
        batch_label_extra = batch_label_extra.applymap(lambda x: str(x).rstrip(' '))
        batch_label_extra['Name'] = batch_label_extra['Name'].str.replace(' ', '_')
        
        #Tidy Name columns in batch-corrected datasets
        final_intra = final_intra.applymap(lambda x: str(x).rstrip('_R'))
        final_intra = final_intra.applymap(lambda x: str(x).rstrip('_RR'))
        final_intra = final_intra.applymap(lambda x: str(x).rstrip(' '))
        final_intra = final_intra.apply(pd.to_numeric, errors = "ignore")
        
        final_extra = final_extra.applymap(lambda x: str(x).rstrip('_R'))
        final_extra = final_extra.applymap(lambda x: str(x).rstrip('_RR'))
        final_extra = final_extra.applymap(lambda x: str(x).rstrip(' '))
        final_extra = final_extra.apply(pd.to_numeric, errors = "ignore")
        
        #Rename fist columns with the sample names
        initial_intra.columns.values[0] = "Name"
        initial_extra.columns.values[0] = "Name"
        final_intra.columns.values[0] = "Name"
        final_extra.columns.values[0] = "Name"
        
        #Only keep the Samples and PC1 and PC2 columns
        initial_intra = initial_intra.iloc[:, [0,1,2]]
        initial_extra = initial_extra.iloc[:, [0,1,2]]
        final_intra = final_intra.iloc[:, [0,1,2]]
        final_extra = final_extra.iloc[:, [0,1,2]]
        
        #Match batch labels to sample names in PCA scores data
        initial_intra = pd.merge(initial_intra, batch_label_intra, on='Name', how='inner')
        final_intra = pd.merge(final_intra, batch_label_intra, on='Name', how='inner')
        initial_extra = pd.merge(initial_extra, batch_label_extra, on='Name', how='inner')
        final_extra = pd.merge(final_extra, batch_label_extra, on='Name', how='inner')
        
        #Plot the 2D PCA plots
        pca_scores_plot_initial_intra = px.scatter(initial_intra, x='PC1', 
                                                   y='PC2',
                                                   color=initial_intra['Batch'],
                                                   #hover_data = components_initial["Sample"],
                                                   title=f'Total Explained Variance: {initial_intra_Var_PC1+initial_intra_Var_PC2:.1f}%',
                                                   labels={'PC1': f"PC1 ({initial_intra_Var_PC1:.1f}%)",
                                                           'PC2': f"PC2 ({initial_intra_Var_PC2:.1f}%)"}, 
                                                   hover_data = ['Name'],
                                                   #category_orders={"Batch": ["B1", "B2"]}
                                                  )
        pca_scores_plot_initial_intra.update_xaxes(range=[-30, 40])
        pca_scores_plot_initial_intra.update_yaxes(range=[-30, 30])
        
        pca_scores_plot_final_intra = px.scatter(final_intra, x='PC1', 
                                                   y='PC2',
                                                   color=final_intra['Batch'],
                                                   #hover_data = components_initial["Sample"],
                                                   title=f'Total Explained Variance: {final_intra_Var_PC1+final_intra_Var_PC2:.1f}%',
                                                   labels={'PC1': f"PC1 ({final_intra_Var_PC1:.1f}%)",
                                                           'PC2': f"PC2 ({final_intra_Var_PC2:.1f}%)"}, 
                                                   hover_data = ['Name'],
                                                   #category_orders={"Batch": ["B1", "B2"]}
                                                  )
        pca_scores_plot_final_intra.update_xaxes(range=[-30, 40])
        pca_scores_plot_final_intra.update_yaxes(range=[-30, 30])
        
        pca_scores_plot_initial_extra = px.scatter(initial_extra, x='PC1', 
                                                   y='PC2',
                                                   color=initial_extra['Batch'],
                                                   #hover_data = components_initial["Sample"],
                                                   title=f'Total Explained Variance: {initial_extra_Var_PC1+initial_extra_Var_PC2:.1f}%',
                                                   labels={'PC1': f"PC1 ({initial_extra_Var_PC1:.1f}%)",
                                                           'PC2': f"PC2 ({initial_extra_Var_PC2:.1f}%)"}, 
                                                   hover_data = ['Name'],
                                                   #category_orders={"Batch": ["B1", "B2"]}
                                                  )
        pca_scores_plot_initial_extra.update_xaxes(range=[-40, 20])
        pca_scores_plot_initial_extra.update_yaxes(range=[-20, 30])
        
        pca_scores_plot_final_extra = px.scatter(final_extra, x='PC1', 
                                                   y='PC2',
                                                   color=final_extra['Batch'],
                                                   #hover_data = components_initial["Sample"],
                                                   title=f'Total Explained Variance: {final_extra_Var_PC1+final_extra_Var_PC2:.1f}%',
                                                   labels={'PC1': f"PC1 ({final_extra_Var_PC1:.1f}%)",
                                                           'PC2': f"PC2 ({final_extra_Var_PC2:.1f}%)"}, 
                                                   hover_data = ['Name'],
                                                   #category_orders={"Batch": ["B1", "B2"]}
                                                  )
        pca_scores_plot_final_extra.update_xaxes(range=[-40, 20])
        pca_scores_plot_final_extra.update_yaxes(range=[-20, 30])

    return pca_scores_plot_initial_intra, pca_scores_plot_final_intra, pca_scores_plot_initial_extra, pca_scores_plot_final_extra
    
@callback(
    Output("download-raw-transposed_UPLOADDATA", "data"),
    [Input("btn-download-raw-transposed_UPLOADDATA", "n_clicks"),
     Input("btn-download-raw-transposed-inTab_UPLOADDATA", "n_clicks"),
     State("store-raw-transposed-data_UPLOADDATA", "data")],
    prevent_initial_call=True,
)
def raw_transposed_data_download_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.raw_transposed_data_download(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_raw_data.xlsx")

#Download selected filtered + normalised file as .csv
@callback(
    Output("download-norm_UPLOADDATA", "data"),
    [Input("btn-download-norm_UPLOADDATA", "n_clicks"),
     Input("btn-download-norm-inTab_UPLOADDATA", "n_clicks"),
     State("store-data_UPLOADDATA", "data")],
    prevent_initial_call=True,
)
def processed_data_download_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.processed_data_download(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_normalised_data.xlsx")
    
#Download PCA scores file with selected samples as .csv
@callback(
    Output("download-pca-scores_UPLOADDATA", "data"),
    [Input("btn-download-pca-scores_UPLOADDATA", "n_clicks"),
     Input("btn-download-pca-scores-inTab_UPLOADDATA", "n_clicks"),
     State("store-data_UPLOADDATA", "data")],
    prevent_initial_call=True,
)
def pca_download_scores_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.pca_download_scores(n_clicks, n_clicks_inTab, data, project_no)
    # pca_download_scores(n_clicks, n_clicks_inTab, data)
    
    return dcc.send_file(f"EdinOmics_{project_no}_pca_scores_results.xlsx")
    
#Download PCA loadings file with selected samples as .csv
@callback(
    Output("download-pca-loadings_UPLOADDATA", "data"),
    [Input("btn-download-pca-loadings_UPLOADDATA", "n_clicks"),
     Input("btn-download-pca-loadings-inTab_UPLOADDATA", "n_clicks"),
     State("store-data_UPLOADDATA", "data")],
    prevent_initial_call=True,
)
def pca_download_loadings_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.pca_download_loadings(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_pca_loadings_results.xlsx")
    
#Download PCA VIP scores file with selected samples as .csv
@callback(
    Output("download-pca-vip-scores_UPLOADDATA", "data"),
    [Input("btn-download-pca-vip-scores_UPLOADDATA", "n_clicks"),
     Input("btn-download-pca-vip-scores-inTab_UPLOADDATA", "n_clicks"),
     State("store-data_UPLOADDATA", "data")],
    prevent_initial_call=True,
)
def pca_download_vip_scores_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.pca_download_vip_scores(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_pca_vip_scores.xlsx")

#Download PLS-DA scores file as .csv
@callback(
    Output("download-plsda-scores_UPLOADDATA", "data"),
    [Input("btn-download-plsda-scores_UPLOADDATA", "n_clicks"),
     Input("btn-download-plsda-scores-inTab_UPLOADDATA", "n_clicks"),
     State("store-data_UPLOADDATA", "data")],
    prevent_initial_call=True,
)
def plsda_scores_download_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.plsda_scores_download(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_pls-da_scores_results.xlsx")
    
#Download PLS-DA loadings file as .csv
@callback(
    Output("download-plsda-loadings_UPLOADDATA", "data"),
    [Input("btn-download-plsda-loadings_UPLOADDATA", "n_clicks"),
     Input("btn-download-plsda-loadings-inTab_UPLOADDATA", "n_clicks"),
     State("store-data_UPLOADDATA", "data")],
    prevent_initial_call=True,
)
def plsda_loadings_download_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.plsda_loadings_download(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_pls-da_loadings_results.xlsx")
    
#Download PLS-DA VIP scores file as .csv
@callback(
    Output("download-plsda-vip-scores_UPLOADDATA", "data"),
    [Input("btn-download-plsda-vip-scores_UPLOADDATA", "n_clicks"),
     Input("btn-download-plsda-vip-scores-inTab_UPLOADDATA", "n_clicks"),
     State("store-data_UPLOADDATA", "data")],
    prevent_initial_call=True,
)
def plsda_vip_scores_download_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.plsda_vip_scores_download(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_pls-da_vip_scores.xlsx")
