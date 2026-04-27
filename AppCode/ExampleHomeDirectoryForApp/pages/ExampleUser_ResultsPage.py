#Page to show tables with raw + filtered data

import dash
from dash import html, callback, Input, Output, dash_table, dcc, State, ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
#Import the functions specified in ReportFunctions.py
import ReportFunctions


#TODO: Update for each individual user account
accountIndexPage = "/AddYourOwnHef"
#TODO: Update for each individual page
page_name = "Experimental Results Example"

mainDataset = 'ExampleData-MetabolomicsResults.csv'
#Some Metabolomics datasets can be HUGE and there may be cases where the user only wants to view a subset of it
# --> to improve webpage speed, used samplesLabels to initially only load in the sample names and group labels
# --> user can use these to select which samples will be analysed, and the main dataset can be subset quickly upon uploading it to reduce memory burden
samplesLabels = 'ExampleData-SamplesAndLabels.csv' 

dash.register_page(__name__, 
                   name = page_name,
                   #TODO: Update for each individual page
                   path="/AddYourOwnResultsPath", 
                   order = 1
                   )

#TODO: Update for each individual project
project_no = "ProjectNo"

#TODO: Update the id suffixes for each individual page
#Otherwise, duplicate callback names (even if in different user reports) will crash Dash Apps 

df_details = pd.read_csv(samplesLabels)
#Create a sample list
sample_list = list(df_details["Sample"])
#Create a label list
label_list = list(df_details["Label"].unique())

p_value_data = pd.DataFrame(data={'p-value': [0.05, 0.01, 0.001], 
                                  'p-value(-log10)': [1.3, 2, 3]})

fc_value_data = pd.DataFrame(data={'FC value': [1.4142, 2, 4], 
                                  ' FC value(log2)': [0.5, 1, 2]})

rawData_tab = dbc.Card(
    dbc.CardBody(
        [
            html.P("Images of your graphs and plots can be directly downloaded when you view them in their respective pages of this report. Simply hover your mouse cursor over your graph and select the camera icon to “Download plot as a png”."),
            html.Br(),
            html.H5("Distribution of Feature Intensities", 
                    style={'textAlign': 'center'}),
            html.P("View the histogram distribution of the frequency of raw metabolite intensities across your selected samples. "),
            dbc.Row([
                dbc.Col([
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "histrogram_raw_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download Raw data", 
                                id = "btn-download-raw-transposed-inTab_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"),
                    # dcc.Graph(id = "histrogram_raw_ExampleReportSuffix")
                    ],
                    lg = {"size":8, "offset":2})
                ]),
            html.H5("Raw Data Table", 
                    style={'textAlign': 'center'}),
            html.P("View the raw data metabolite peak intensities for each sample and group (“Label”). Note: the data processing software automatically assigns metabolites not detected in a particular sample as 0.001.", className="card-text"),
            dbc.Spinner(
                children=[
                    html.Div(id='display_subset_raw_tabs_ExampleReportSuffix'),
                    ],
                size = "lg", 
                color = "primary", 
                fullscreen = True
                ),
            # html.Div(id='display_subset_raw_tabs_ExampleReportSuffix'),
        ]
    ),
    className="mt-3",
)

normData_tab = dbc.Card(
    dbc.CardBody(
        [
            html.P("Images of your graphs and plots can be directly downloaded when you view them in their respective pages of this report. Simply hover your mouse cursor over your graph and select the camera icon to “Download plot as a png”."),
            html.Br(),
            html.H5("Distribution of Feature Intensities", 
                    style={'textAlign': 'center'}),
            html.P("View the histogram distribution of the frequency of normalised metabolite intensities across your selected samples. Note: these should have an overall normal/Gaussian distribution, appropriate for performing statistical analyses with."),
            dbc.Row([
                dbc.Col([
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "histogram_norm_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download Normalised data", 
                                id = "btn-download-norm-inTab_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"),
                    # dcc.Graph(id = "histogram_norm_ExampleReportSuffix")
                    ],
                    lg = {"size":8, "offset":2})
                ]),
            html.H5("Normalised Data Table", 
                    style={'textAlign': 'center'}),
            html.P("View the normalised metabolite peak intensities for each sample and group (“Label”). Note: if any metabolites are not detected in your sample selection, these are removed from the selected dataset as those would otherwise introduce “Divide by 0” errors during the Pareto scaling.", className="card-text"),
            dbc.Spinner(
                children=[
                    html.Div(id='display_subset_tabs_ExampleReportSuffix'),
                    ],
                size = "lg", 
                color = "primary", 
                fullscreen = True
                ),
            # html.Div(id='display_subset_tabs_ExampleReportSuffix'),
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
            dcc.Markdown("""PCA is an *unsupervised* linear dimensionality reduction technique. Simply, Scikit Learn’s PCA functions are used to convert the correlations/non-correlations in the normalised metabolite intensity data into Principal Components that can be viewed in two dimensions. Samples that are highly correlated will cluster together and those that are not will be spread apart from each other. Each Component is ranked: differences along the first Principal Component axis (PC1) are more important that the differences along the second principal component axis (PC2)."""),
            html.P("Images of your graphs and plots can be directly downloaded when you view them in their respective pages of this report. Simply hover your mouse cursor over your graph and select the camera icon to “Download plot as a png”."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H5("PCA scores plot", 
                            style={'textAlign': 'center'}),
                    html.P("View how each of your selected samples are similar/dissimilar to each other. The percentages on each axis represent the variation ratio of each component. The circles represent 95% confidence intervals for the samples in each group."),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_scores_plot_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download PCA scores data", 
                                id = "btn-download-pca-scores-inTab_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"
                                ),
                    # dcc.Graph(id = "pca_scores_plot_ExampleReportSuffix")
                    ], lg={"size":6}
                    ), 
                dbc.Col([
                    html.H5("PCA loadings plot", 
                            style={'textAlign': 'center'}),
                    html.P("View the metabolites that are driving the variation observed in the Scores plot. Hover over the data points to show metabolites. You can select these datapoints to view their raw and normalised abundances in the metabolite selection plots below."),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_loadings_plot_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download PCA loadings data", 
                                id = "btn-download-pca-loadings-inTab_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"),
                    # dcc.Graph(id = "pca_loadings_plot_ExampleReportSuffix")
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
                            dcc.Graph(id = "pca_metabolite_select_raw_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    # dcc.Graph(id = "pca_metabolite_select_raw_ExampleReportSuffix")
                    ], 
                    lg={"size":6}
                    ),
                dbc.Col([
                    html.H5("Normalised data", style={'textAlign': 'center'}),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_metabolite_select_norm_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    # dcc.Graph(id = "pca_metabolite_select_norm_ExampleReportSuffix")
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
                            dcc.Graph(id = "pca_vip_plot_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download PCA VIP Scores", 
                                id = "btn-download-pca-vip-scores-inTab_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"),
                    # dcc.Graph(id = "pca_vip_plot_ExampleReportSuffix")
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
                            dcc.Graph(id = "pca_group_avg_heatmap_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    # dcc.Graph(id = "pca_group_avg_heatmap_ExampleReportSuffix")
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
                    dcc.Dropdown(id = "pca_any_metab_selection_ExampleReportSuffix", multi = True)
                ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Update selected metabolite plots", 
                                id = "btn-update-pca-any-metab-sele_ExampleReportSuffix", 
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
                        id='pca_raw_plot_type_sele_ExampleReportSuffix', 
                        options=['Bar Plot', 'Box Plot', 'Violin Plot'],
                        value='Bar Plot'
                        ),
                    html.Br(), 
                    html.P("Y-axis scale:"),
                    dcc.RadioItems(
                        id='pca_raw_plot_yaxis_sele_ExampleReportSuffix', 
                        options=['Linear', 'Log10'],
                        value='Linear'
                        ),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "pca_any_metab_raw_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    # dcc.Graph(id = "pca_any_metab_raw_ExampleReportSuffix")
                    ], 
                    lg={"size":6}
                    ),
                dbc.Col([
                    html.H5("Normalised Data", style = {'textAlign':'center'}), 
                    html.P("Plot Type:"),
                    dcc.RadioItems(
                        id='pca_norm_plot_type_sele_ExampleReportSuffix', 
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
                            dcc.Graph(id = "pca_any_metab_norm_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    # dcc.Graph(id = "pca_any_metab_norm_ExampleReportSuffix")
                    ], 
                    lg={"size":6}
                    )
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
                            dcc.Graph(id = "interactive_plsda_plot_2D_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download PLS-DA scores data", 
                                id = "btn-download-plsda-scores-inTab_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"),
                    # dcc.Graph(id = "interactive_plsda_plot_2D_ExampleReportSuffix")
                    ], lg = {"size":6}
                    ), 
                dbc.Col([
                    html.H5("PLS-DA loadings plot", 
                            style={'textAlign': 'center'}),
                    html.P("View the metabolites that are driving the variation observed in the Scores plot. Hover over the data points to show metabolites. Select these datapoints to view their raw and normalised abundances in the metabolite selection plots below."),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "plsda_loadings_plot_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download PLS-DA loadings data", 
                                id = "btn-download-plsda-loadings-inTab_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary")
                    # dcc.Graph(id = "plsda_loadings_plot_ExampleReportSuffix")
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
                            dcc.Graph(id = "plsda_metabolite_select_raw_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    # dcc.Graph(id = "plsda_metabolite_select_raw_ExampleReportSuffix")
                    ], 
                    lg={"size":6}
                    ),
                dbc.Col([
                    html.H5("Normalised data", style={'textAlign': 'center'}),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "plsda_metabolite_select_norm_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    # dcc.Graph(id = "plsda_metabolite_select_norm_ExampleReportSuffix")
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
                            dcc.Graph(id = "plsda_vip_plot_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    dbc.Button("Download PLS-DA VIP Scores", 
                                id = "btn-download-plsda-vip-scores-inTab_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"),
                    # dcc.Graph(id = "plsda_vip_plot_ExampleReportSuffix")
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
                            dcc.Graph(id = "plsda_group_avg_heatmap_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = True
                        ),
                    # dcc.Graph(id = "plsda_group_avg_heatmap_ExampleReportSuffix")
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
                    dcc.Dropdown(id = "plsda_any_metab_selection_ExampleReportSuffix", multi = True)
                ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Update selected metabolite plots", 
                                id = "btn-update-plsda-any-metab-sele_ExampleReportSuffix", 
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
                        id='plsda_raw_plot_type_sele_ExampleReportSuffix', 
                        options=['Bar Plot', 'Box Plot', 'Violin Plot'],
                        value='Bar Plot'
                        ),
                    html.Br(), 
                    html.P("Y-axis scale:"),
                    dcc.RadioItems(
                        id='plsda_raw_plot_yaxis_sele_ExampleReportSuffix', 
                        options=['Linear', 'Log10'],
                        value='Linear'
                        ),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "plsda_any_metab_raw_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    # dcc.Graph(id = "plsda_any_metab_raw_ExampleReportSuffix")
                    ], 
                    lg={"size":6}
                    ),
                dbc.Col([
                    html.H5("Normalised Data", style = {'textAlign':'center'}), 
                    html.P("Plot Type:"),
                    dcc.RadioItems(
                        id='plsda_norm_plot_type_sele_ExampleReportSuffix', 
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
                            dcc.Graph(id = "plsda_any_metab_norm_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    # dcc.Graph(id = "plsda_any_metab_norm_ExampleReportSuffix")
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
            html.P("Select samples group to compare against each other, where the selection in “Group 1” will be analysed against those in “Group 2”. Click “Update volcano plot” to view your results. The Fold-Change is calculated with the raw data and the p-value is calculated with the normalised data. Hover over a data point to see which metabolite it is and whether it is elevated in Group 1 or 2."),
            html.P("Images of your graphs and plots can be directly downloaded when you view them in their respective pages of this report. Simply hover your mouse cursor over your graph and select the camera icon to “Download plot as a png”."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H5("Group 1"), 
                    dcc.Dropdown(id="group-1-options_ExampleReportSuffix", multi=True)
                    ],
                    xs = {"size":12, "offset":0}, 
                    md = {"size":6, "offset":0}
                    ),
                dbc.Col([
                    html.H5("Group 2"), 
                    dcc.Dropdown(id="group-2-options_ExampleReportSuffix", multi=True)
                    ],
                    xs = {"size":12, "offset":0}, 
                    md = {"size":6, "offset":0}
                    )
                ]),
            html.Br(), 
            html.H6("p-value threshold"),
            dbc.Row([
                dbc.Col([
                    html.P("To add a p-value significance threshold to your volcano plot: Enter a numeric value in the text box provided. For reference, the -log10 (scale of y axis) products for commonly used p-value thresholds are provided in the table shown:"),
                    ], 
                    md = 6),
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
            dcc.Input(id="volcano_sig_thres_ExampleReportSuffix", type="number", 
                      placeholder="Add p-value threshold"),
            html.Br(),
            html.Br(),
            html.H6("Fold-Change (FC) threshold"),
            dbc.Row([
                dbc.Col([
                    html.P("To add a Fold-Change threshold to your volcano plot: Enter a numeric value in the text box provided. For reference, the log2 (scale of x axis) products for commonly used FC thresholds are provided in the table shown:")
                    ], 
                    md = 6),
                dbc.Col([
                    dash_table.DataTable(data = fc_value_data.to_dict('records'), 
                                         columns=[{'id': c, 'name': c} for c in fc_value_data.columns],
                                         style_cell = { 
                                             "font_family":"sans-serif"
                                             }
                                         ),
                    ], 
                    xs = 3, 
                    md = 2)
                ]),
            dcc.Input(id="volcano_FC_thres_ExampleReportSuffix", type="number", 
                      placeholder="Add FC threshold"),
            html.Br(),
            html.Br(),
            dcc.Checklist(id = "volcano_SigLabels_Checkbox_ExampleReportSuffix", 
                          options = [' Add metabolite name labels to the data points']),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Update volcano plot", 
                                id = "btn-update-volcano-plot_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"),
                    ])
                ]),
            html.Br(),
            html.P("To view the labels for clustered data points, drag your mouse across a selected area of your volcano plot to zoom in. When the mouse is hovering over the graph, you can select the house-shaped icon to reset the axes back to their original format."),
            html.Br(),
            dbc.Row([
                dbc.Spinner(
                    children=[
                        dcc.Graph(id = "volano-plot_ExampleReportSuffix")
                        ],
                    size = "lg", 
                    color = "primary", 
                    fullscreen = False
                    ),
                # dcc.Graph(id = "volano-plot_ExampleReportSuffix")
                ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Download Volcano Plot Data", 
                                id = "btn-download-volcano-data_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"),
                    dcc.Download(id = "volano_data_to_download_ExampleReportSuffix"),
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
                            dcc.Graph(id = "volcano_metabolite_select_raw_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    # dcc.Graph(id = "volcano_metabolite_select_raw_ExampleReportSuffix")
                    ], 
                    lg={"size":6}
                    ),
                dbc.Col([
                    html.H5("Normalised data", style={'textAlign': 'center'}),
                    dbc.Spinner(
                        children=[
                            dcc.Graph(id = "volcano_metabolite_select_norm_ExampleReportSuffix")
                            ],
                        size = "lg", 
                        color = "primary", 
                        fullscreen = False
                        ),
                    # dcc.Graph(id = "volcano_metabolite_select_norm_ExampleReportSuffix")
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
                        id = "customHeatmap_btn_allMetab_ExampleReportSuffix", 
                        n_clicks = 0
                        ),
                    dbc.Button(
                        'Clear all metabolites', 
                        id = "customHeatmap_btn_ClearMetab_ExampleReportSuffix", 
                        n_clicks = 0
                        ),
                    ])
                ]),
            dbc.Row([
                dbc.Col([
                    html.H5("Select Sample Groups"),
                    dcc.Dropdown(id = "customHeatmap_GroupSele_ExampleReportSuffix", 
                                 multi = True)
                    ], 
                    xs = {"size":12, "offset":0}, 
                    md = {"size":6, "offset":0}
                    ), 
                dbc.Col([
                    html.H5("Select Metabolites"), 
                    dcc.Dropdown(id = "customHeatmap_MetaboliteSele_ExampleReportSuffix", 
                                 multi = True)
                    ])
                ]), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Update Heatmap", 
                                id = "btn_update_customHeatmap_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"),
                    ])
                ]),
            html.Br(),
            dbc.Spinner(
                children=[
                    dcc.Graph(id = "customHeatmap_heatmap_ExampleReportSuffix")
                    ],
                size = "lg", 
                color = "primary", 
                fullscreen = False
                ),
            # dcc.Graph(id = "customHeatmap_heatmap_ExampleReportSuffix")
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
            html.P("Images of your graphs and plots can also be directly downloaded when you view them in their respective pages of this report. Simply hover your mouse cursor over your graph and select the camera icon to “Download plot as a png”."),
            html.H5("Data Tables"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Raw data", 
                                id = "btn-download-raw-transposed_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"),
                    dcc.Download(id = "download-raw-transposed_ExampleReportSuffix")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":2}
                    ),
                dbc.Col([
                    dbc.Button("Normalised data", 
                                id = "btn-download-norm_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-norm_ExampleReportSuffix")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":3, "offset":1}
                    ),
                ]),
            html.H5("PCA Data"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("PCA scores data", 
                                id = "btn-download-pca-scores_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"
                                ), 
                    dcc.Download(id = "download-pca-scores_ExampleReportSuffix")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":1}
                    ),
                dbc.Col([
                    dbc.Button("PCA loadings data", 
                                id = "btn-download-pca-loadings_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-pca-loadings_ExampleReportSuffix")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":1}
                    ),
                dbc.Col([
                    dbc.Button("PCA VIP Scores", 
                                id = "btn-download-pca-vip-scores_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-pca-vip-scores_ExampleReportSuffix")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":1}
                    ),
                ]),
            html.H5("PLS-DA Data"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("PLS-DA scores data", 
                                id = "btn-download-plsda-scores_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-plsda-scores_ExampleReportSuffix")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":2}
                    ),
                dbc.Col([
                    dbc.Button("PLS-DA loadings data", 
                                id = "btn-download-plsda-loadings_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-plsda-loadings_ExampleReportSuffix")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":2}
                    ),
                dbc.Col([
                    dbc.Button("PLS-DA VIP Scores", 
                                id = "btn-download-plsda-vip-scores_ExampleReportSuffix", 
                                className="mb-3",
                                color="primary"), 
                    dcc.Download(id = "download-plsda-vip-scores_ExampleReportSuffix")
                    ], 
                    xs = {"size":12, "offset":0}, 
                    #md = {"size":2, "offset":1}
                    ),
                ])
        ]
    ),
    className="mt-3",
)


layout = html.Div([
    #Save Data in the memory + allow to be shared between functions/tabs
    dcc.Link("Go back to view other reports", href=accountIndexPage),
    html.Br(),
    html.H5("{}".format(page_name), style={'textAlign': 'center'}),
    dbc.Spinner(
        children=[
            dcc.Store(id = "store-data_ExampleReportSuffix", 
                      data = [], 
                      storage_type = "memory"),
            ],
        size = "lg", 
        color = "primary", 
        fullscreen = True
        ),
    dbc.Spinner(
        children=[
            dcc.Store(id = "store-raw-transposed-data_ExampleReportSuffix", 
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
                id="btn_group_collapse_0_ExampleReportSuffix", 
                #color = "info",
                n_clicks = 0
                ), 
            dbc.Collapse(
                dcc.Dropdown(
                    id = "label_selection_ExampleReportSuffix",
                    options = label_list, 
                    value = label_list, 
                    multi = True, 
                    #style = {"overflow-y":"scroll", "height": "280px"}
                    ), 
                id="group_list_collapse_ExampleReportSuffix", 
                is_open=False
                )
            ], 
            xs = {"size":12, "offset":0},
            md = {"size":6, "offset":0}), 
        dbc.Col([
            dbc.Button(
                'Click here to select individual samples', 
                id="btn_individual_collapse_0_ExampleReportSuffix", 
                #color = "info",
                n_clicks = 0
                ), 
            dbc.Collapse(
                dcc.Dropdown(
                    id = "sample_selection_ExampleReportSuffix",
                    options = sample_list, 
                    value = sample_list, 
                    multi = True, 
                    #style = {"overflow-y":"scroll", "height": "280px"}
                    ), 
                id="individual_list_collapse_ExampleReportSuffix", 
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
                        id = "btn-update-form_data0_ExampleReportSuffix", 
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

#Display Sample groups to select when button clicked
@callback(
    Output("group_list_collapse_ExampleReportSuffix", "is_open"), 
    Input("btn_group_collapse_0_ExampleReportSuffix", "n_clicks"), 
    State("group_list_collapse_ExampleReportSuffix", "is_open")
    )
def toggle_group_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

#Display individual samples to select when button clicked
@callback(
    Output("individual_list_collapse_ExampleReportSuffix", "is_open"), 
    Input("btn_individual_collapse_0_ExampleReportSuffix", "n_clicks"), 
    State("individual_list_collapse_ExampleReportSuffix", "is_open")
    )
def toggle_individual_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

#Subset data frame + save in memory storage
@callback(
    [Output('store-data_ExampleReportSuffix', "data"),
     Output('store-raw-transposed-data_ExampleReportSuffix', "data"),
     Output('pca_any_metab_selection_ExampleReportSuffix', 'options'),
     Output('plsda_any_metab_selection_ExampleReportSuffix', 'options'),
     ],
    [Input("btn-update-form_data0_ExampleReportSuffix", "n_clicks"),
     State("label_selection_ExampleReportSuffix", "value"),
     State("sample_selection_ExampleReportSuffix", "value")]
    )
def update_data_scriptInitiate(n_clicks, value_label, value_sample):
    
    df_sel, df_raw_transposed, pca_metabolite_list, plsda_metabolite_list = ReportFunctions.update_data(n_clicks, value_label, 
                                                                             value_sample, mainDataset)
    
    return df_sel.to_dict("records"), df_raw_transposed.to_dict("records"), pca_metabolite_list, plsda_metabolite_list

#Display raw data table
@callback(
    [Output("display_subset_raw_tabs_ExampleReportSuffix", "children"), 
     Output("histrogram_raw_ExampleReportSuffix", "figure")
     ],
    Input("store-raw-transposed-data_ExampleReportSuffix", "data"),
    ) 
def update_raw_table_scriptInitiate(data):
    
    overview_table, hist_raw = ReportFunctions.update_raw_table(data)
    
    return overview_table, hist_raw

#Display normalised data table
@callback(
    [Output('display_subset_tabs_ExampleReportSuffix', "children"),
     Output("histogram_norm_ExampleReportSuffix", "figure")
     ],
    Input("store-data_ExampleReportSuffix", "data"),
    )
def update_normalised_table_scriptInitiate(data):
    
    overview_table, hist_norm = ReportFunctions.update_normalised_table(data)
    
    return overview_table, hist_norm

#Interactive PCA plots (including PCA VIP and Heat Map)
@callback(
    [Output("pca_scores_plot_ExampleReportSuffix", "figure"),
    Output("pca_loadings_plot_ExampleReportSuffix", "figure"),
    Output("pca_vip_plot_ExampleReportSuffix", "figure"), 
    Output("pca_group_avg_heatmap_ExampleReportSuffix", "figure")
    ],
    [Input("store-data_ExampleReportSuffix", "data"), 
     State("label_selection_ExampleReportSuffix", "value")
     ],
)
def update_pca_scriptInitialise(data, value_label):
    
    pca_scores_plot, pca_loadings_plot, vip_plot_pca, heatmap_mean_pca = ReportFunctions.update_pca_UserGroupOrder(data, value_label)
    
    return pca_scores_plot, pca_loadings_plot, vip_plot_pca, heatmap_mean_pca

#Select metabolite from loadings plot
@callback(
    Output('pca_metabolite_select_raw_ExampleReportSuffix', 'figure'),
     Output("pca_metabolite_select_norm_ExampleReportSuffix", "figure"),
    [Input('pca_loadings_plot_ExampleReportSuffix', 'clickData'),
     Input("store-raw-transposed-data_ExampleReportSuffix", "data"), 
     Input("store-data_ExampleReportSuffix", "data")
     ], 
    State("label_selection_ExampleReportSuffix", "value"),
    )
def update_average_plots_pca_scriptInitialise(clickData, df_raw_T, df_norm, value_label):
    
    fig_raw_pca, fig_norm_pca = ReportFunctions.update_average_plots_pca_UserGroupOrder(clickData, df_raw_T, df_norm, value_label)
    
    return fig_raw_pca, fig_norm_pca

#Update metabolite selection plots (PCA tab)
@callback(
    Output('pca_any_metab_raw_ExampleReportSuffix', 'figure'), 
    Output('pca_any_metab_norm_ExampleReportSuffix', 'figure'), 
    Input('btn-update-pca-any-metab-sele_ExampleReportSuffix', 'n_clicks'),
    Input('store-raw-transposed-data_ExampleReportSuffix', 'data'), 
    Input('store-data_ExampleReportSuffix', 'data'), 
    Input('pca_raw_plot_type_sele_ExampleReportSuffix', 'value'),
    Input('pca_raw_plot_yaxis_sele_ExampleReportSuffix', 'value'),
    Input('pca_norm_plot_type_sele_ExampleReportSuffix', 'value'),
    State('pca_any_metab_selection_ExampleReportSuffix', 'value'), 
    State("label_selection_ExampleReportSuffix", "value"),
)
def pca_any_metab_plots_scriptInitialise(n_clicks, data_raw, data_norm, rawplot_type, rawplot_axis, normplot_type, metabolite_name, value_label):
    
    pca_any_metab_raw_fig, pca_any_metab_norm_fig = ReportFunctions.pca_any_metab_plots_UserGroupOrder(n_clicks, 
                                                                        data_raw, data_norm, rawplot_type, 
                                                                        rawplot_axis, normplot_type, metabolite_name, 
                                                                        value_label)
    
    return pca_any_metab_raw_fig, pca_any_metab_norm_fig

#Interactive PLS-DA plots
@callback(
    [Output("interactive_plsda_plot_2D_ExampleReportSuffix", "figure"), 
    Output("plsda_loadings_plot_ExampleReportSuffix", "figure"), 
    Output("plsda_vip_plot_ExampleReportSuffix", "figure"), 
    Output("plsda_group_avg_heatmap_ExampleReportSuffix", "figure")
    ],
    [Input("store-data_ExampleReportSuffix", "data")],
    State("label_selection_ExampleReportSuffix", "value"),
)
def update_plsda_scriptInitialise(data, value_label):
    
    interactive_plsda_plot_2D, plsda_loadings_plot, vip_plot_plsda, heatmap_mean_plsda = ReportFunctions.update_plsda_UserGroupOrder(data, value_label)
    
    return interactive_plsda_plot_2D, plsda_loadings_plot, vip_plot_plsda, heatmap_mean_plsda

#Select metabolite from loadings plot
@callback(
    Output('plsda_metabolite_select_raw_ExampleReportSuffix', 'figure'),
     Output("plsda_metabolite_select_norm_ExampleReportSuffix", "figure"),
    [Input('plsda_loadings_plot_ExampleReportSuffix', 'clickData'),
     Input("store-raw-transposed-data_ExampleReportSuffix", "data"), 
     Input("store-data_ExampleReportSuffix", "data")
     ], 
    State("label_selection_ExampleReportSuffix", "value"),
    )
def update_average_plots_plsda_scriptInitialise(clickData, df_raw_T, df_norm, value_label):
    
    fig_raw_plsda, fig_norm_plsda = ReportFunctions.update_average_plots_plsda_UserGroupOrder(clickData, df_raw_T, df_norm, value_label)
    
    return fig_raw_plsda, fig_norm_plsda

#Update metabolite selection plots (PLSDA)
@callback(
    Output('plsda_any_metab_raw_ExampleReportSuffix', 'figure'), 
    Output('plsda_any_metab_norm_ExampleReportSuffix', 'figure'), 
    Input('btn-update-plsda-any-metab-sele_ExampleReportSuffix', 'n_clicks'),
    Input('store-raw-transposed-data_ExampleReportSuffix', 'data'), 
    Input('store-data_ExampleReportSuffix', 'data'), 
    Input('plsda_raw_plot_type_sele_ExampleReportSuffix', 'value'),
    Input('plsda_raw_plot_yaxis_sele_ExampleReportSuffix', 'value'),
    Input('plsda_norm_plot_type_sele_ExampleReportSuffix', 'value'),
    State('plsda_any_metab_selection_ExampleReportSuffix', 'value'), 
    State("label_selection_ExampleReportSuffix", "value"),
)
def plsda_any_metab_plots_scriptInitialise(n_clicks, data_raw, data_norm, rawplot_type, rawplot_axis, normplot_type, metabolite_name, value_label):
    
    plsda_any_metab_raw_fig, plsda_any_metab_norm_fig = ReportFunctions.plsda_any_metab_plots_UserGroupOrder(n_clicks, 
                                                                              data_raw, data_norm, rawplot_type, 
                                                                              rawplot_axis, normplot_type, 
                                                                              metabolite_name, value_label)
    
    return plsda_any_metab_raw_fig, plsda_any_metab_norm_fig

#Create selection lists from data in memory (for volcano plot)
@callback(
    Output("group-1-options_ExampleReportSuffix", "options"),
    Output("group-2-options_ExampleReportSuffix", "options"),
    Input("store-raw-transposed-data_ExampleReportSuffix", "data"),
)
def group_options(data):
    if data is None:
        raise PreventUpdate
    else:
        df = pd.DataFrame(data)
        
        #Remove QCs, blanks, and standards from Volcano Plot selection
        #TODO: May want to update for each dataset
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
    Output("volano-plot_ExampleReportSuffix", "figure"),
    Input("btn-update-volcano-plot_ExampleReportSuffix", "n_clicks"),
    State("store-raw-transposed-data_ExampleReportSuffix", "data"),
    State("group-1-options_ExampleReportSuffix", "value"),
    State("group-2-options_ExampleReportSuffix", "value"), 
    State("volcano_sig_thres_ExampleReportSuffix", "value"),
    State("volcano_FC_thres_ExampleReportSuffix", "value"), 
    State("volcano_SigLabels_Checkbox_ExampleReportSuffix", "value")
)
def volcanic_eruption_scriptInitialise(n_clicks, data, state_1, state_2, sig_thres, fc_thres, labelYes):
    
    volcano_plot = ReportFunctions.volcanic_eruption_FCThreshold(n_clicks, data, state_1, state_2, sig_thres, fc_thres, labelYes)
    
    return volcano_plot

#Create selection lists from data in memory (for custom Heatmap)
@callback(
    Output("customHeatmap_GroupSele_ExampleReportSuffix", "options"),
    Output("customHeatmap_MetaboliteSele_ExampleReportSuffix", "options"),
    Output("customHeatmap_MetaboliteSele_ExampleReportSuffix", "value"),
    Input("store-data_ExampleReportSuffix", "data"),
    Input("customHeatmap_btn_allMetab_ExampleReportSuffix", "n_clicks"),
    Input("customHeatmap_btn_ClearMetab_ExampleReportSuffix", "n_clicks"), 
    prevent_initial_call=True,
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
        if "customHeatmap_btn_allMetab_ExampleReportSuffix" == ctx.triggered_id:
            
            value_MetaboliteSele = MetaboliteSele.copy()
            
            return SampleSele, MetaboliteSele, value_MetaboliteSele
        
        #If not all metabolites are selected: make the dropdown value nothing
        elif "customHeatmap_btn_ClearMetab_ExampleReportSuffix" == ctx.triggered_id:
            
            value_MetaboliteSele = []
            
            return SampleSele, MetaboliteSele, value_MetaboliteSele
        
        # else:
        elif "customHeatmap_btn_ClearMetab_ExampleReportSuffix" != ctx.triggered_id or "customHeatmap_btn_allMetab_ExampleReportSuffix" != ctx.triggered_id:
            
            value_MetaboliteSele = []
            
            return SampleSele, MetaboliteSele, value_MetaboliteSele

#Create custom heatmaps
@callback(
    Output("customHeatmap_heatmap_ExampleReportSuffix", "figure"),
     Input("btn_update_customHeatmap_ExampleReportSuffix", "n_clicks"),
     State("store-data_ExampleReportSuffix", "data"), 
     State("customHeatmap_GroupSele_ExampleReportSuffix", "value"), 
     State("customHeatmap_MetaboliteSele_ExampleReportSuffix", "value")
)
def CustomHeatmap_scriptInitialise(n_clicks, data, SelectedGroups, SelectedMetabolites):
    
    custom_heatmap = ReportFunctions.CustomHeatmap(n_clicks, data, SelectedGroups, SelectedMetabolites)
    
    return custom_heatmap

#Download volcano plot data
@callback(
    Output("volano_data_to_download_ExampleReportSuffix", "data"),
    Input("btn-download-volcano-data_ExampleReportSuffix", "n_clicks"),
    Input("store-raw-transposed-data_ExampleReportSuffix", "data"),
    State("group-1-options_ExampleReportSuffix", "value"),
    State("group-2-options_ExampleReportSuffix", "value"), 
    Input("volcano_sig_thres_ExampleReportSuffix", "value"),
    Input("store-data_ExampleReportSuffix", "data")
)
def volcanic_eruption_download_scriptInitialise(n_clicks, data_raw, state_1, state_2, sig_thres, data_norm):
    
    #Function creates the file to be 'sent' to the user to download in the return function below
    ReportFunctions.volcanic_eruption_download(n_clicks, data_raw, state_1, state_2, sig_thres, data_norm, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_Volcano_plot_data.xlsx")

#Select metabolite from volcano plot
@callback(
    Output('volcano_metabolite_select_raw_ExampleReportSuffix', 'figure'),
     Output("volcano_metabolite_select_norm_ExampleReportSuffix", "figure"),
    [Input('volano-plot_ExampleReportSuffix', 'clickData'),
     Input("store-raw-transposed-data_ExampleReportSuffix", "data"), 
     Input("store-data_ExampleReportSuffix", "data")
     ],
    State("group-1-options_ExampleReportSuffix", "value"),
    State("group-2-options_ExampleReportSuffix", "value"), 
    )
def update_average_plots_volcano_scriptInitialise(clickData, df_raw_T, df_norm, state_1, state_2):
    
    fig_raw_volcano, fig_norm_volcano = ReportFunctions.update_average_plots_volcano_SeleData(clickData, df_raw_T, df_norm, state_1, state_2)
    
    return fig_raw_volcano, fig_norm_volcano

#Download raw, transposed data        
@callback(
    Output("download-raw-transposed_ExampleReportSuffix", "data"),
    [Input("btn-download-raw-transposed_ExampleReportSuffix", "n_clicks"),
     Input("btn-download-raw-transposed-inTab_ExampleReportSuffix", "n_clicks"),
     State("store-raw-transposed-data_ExampleReportSuffix", "data")],
    prevent_initial_call=True,
)
def raw_transposed_data_download_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.raw_transposed_data_download(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_raw_data.xlsx")

#Download selected filtered + normalised file as .xlsx file
@callback(
    Output("download-norm_ExampleReportSuffix", "data"),
    [Input("btn-download-norm_ExampleReportSuffix", "n_clicks"),
     Input("btn-download-norm-inTab_ExampleReportSuffix", "n_clicks"),
     State("store-data_ExampleReportSuffix", "data")],
    prevent_initial_call=True,
)
def processed_data_download_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.processed_data_download(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_normalised_data.xlsx")
    
#Download PCA scores file with selected samples as .xlsx
@callback(
    Output("download-pca-scores_ExampleReportSuffix", "data"),
    Input("btn-download-pca-scores_ExampleReportSuffix", "n_clicks"),
    Input("btn-download-pca-scores-inTab_ExampleReportSuffix", "n_clicks"),
    State("store-data_ExampleReportSuffix", "data"),
    prevent_initial_call=True,
)
def pca_download_scores_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.pca_download_scores(n_clicks, n_clicks_inTab, data, project_no)
    # pca_download_scores(n_clicks, n_clicks_inTab, data)
    
    return dcc.send_file(f"EdinOmics_{project_no}_pca_scores_results.xlsx")
    
#Download PCA loadings file with selected samples as .xlsx
@callback(
    Output("download-pca-loadings_ExampleReportSuffix", "data"),
    [Input("btn-download-pca-loadings_ExampleReportSuffix", "n_clicks"),
     Input("btn-download-pca-loadings-inTab_ExampleReportSuffix", "n_clicks"),
     State("store-data_ExampleReportSuffix", "data")],
    prevent_initial_call=True,
)
def pca_download_loadings_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.pca_download_loadings(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_pca_loadings_results.xlsx")
    
#Download PCA VIP scores file with selected samples as .xlsx
@callback(
    Output("download-pca-vip-scores_ExampleReportSuffix", "data"),
    [Input("btn-download-pca-vip-scores_ExampleReportSuffix", "n_clicks"),
     Input("btn-download-pca-vip-scores-inTab_ExampleReportSuffix", "n_clicks"),
     State("store-data_ExampleReportSuffix", "data")],
    prevent_initial_call=True,
)
def pca_download_vip_scores_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.pca_download_vip_scores(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_pca_vip_scores.xlsx")

#Download PLS-DA scores file as .xlsx
@callback(
    Output("download-plsda-scores_ExampleReportSuffix", "data"),
    [Input("btn-download-plsda-scores_ExampleReportSuffix", "n_clicks"),
     Input("btn-download-plsda-scores-inTab_ExampleReportSuffix", "n_clicks"),
     State("store-data_ExampleReportSuffix", "data")],
    prevent_initial_call=True,
)
def plsda_scores_download_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.plsda_scores_download(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_pls-da_scores_results.xlsx")
    
#Download PLS-DA loadings file as .xlsx
@callback(
    Output("download-plsda-loadings_ExampleReportSuffix", "data"),
    [Input("btn-download-plsda-loadings_ExampleReportSuffix", "n_clicks"),
     Input("btn-download-plsda-loadings-inTab_ExampleReportSuffix", "n_clicks"),
     State("store-data_ExampleReportSuffix", "data")],
    prevent_initial_call=True,
)
def plsda_loadings_download_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.plsda_loadings_download(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_pls-da_loadings_results.xlsx")
    
#Download PLS-DA VIP scores file as .xlsx
@callback(
    Output("download-plsda-vip-scores_ExampleReportSuffix", "data"),
    [Input("btn-download-plsda-vip-scores_ExampleReportSuffix", "n_clicks"),
     Input("btn-download-plsda-vip-scores-inTab_ExampleReportSuffix", "n_clicks"),
     State("store-data_ExampleReportSuffix", "data")],
    prevent_initial_call=True,
)
def plsda_vip_scores_download_scriptInitialise(n_clicks, n_clicks_inTab, data):
    
    ReportFunctions.plsda_vip_scores_download(n_clicks, n_clicks_inTab, data, project_no)
    
    return dcc.send_file(f"EdinOmics_{project_no}_pls-da_vip_scores.xlsx")
    