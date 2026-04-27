#Page to show general information and the methods used 

import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from ReportDescriptiveText import StandardRHIMMSMethodText, StandardStatProcessingText
import pandas as pd

#TODO: Update for each individual user account
accountIndexPage = "/AddYourOwnHef"
#TODO: Update for each individual page
page_name = "Experimental Methods Example"

dash.register_page(__name__, 
                   name = page_name,
                   #TODO: Update for each individual page
                   path="/AddYourOwnMethodsPath", 
                   order = 0
                   )

dataset_info = pd.DataFrame(data={
    'Sample Name':["A Ext 1","A Ext 2","A Ext 3","A Int 1","A Int 2","A Int 3",
                  "B Ext 1","B Ext 2","B Ext 3","B Int 1","B Int 2","B Int 3",
                  "C Ext 1","C Ext 2","C Ext 3","C Int 1","C Int 2","C Int 3",
                  "Control Ext 1","Control Ext 2","Control Ext 3","Control Int 1",
                  "Control Int 2","Control Int 3","Blank01","Blank02","Blank03",
                  "QC01","QC02","QC03","QC04","QC05","QCdilution 0_0625",
                  "QCdilution 0_125","QCdilution 0_25","QCdilution 0_5","QCdilution 1_0"
                  ], 
    'Sample Group':["A Ext","A Ext","A Ext","A Int","A Int","A Int","B Ext","B Ext",
                    "B Ext","B Int","B Int","B Int","C Ext","C Ext","C Ext","C Int",
                    "C Int","C Int","Control Ext","Control Ext","Control Ext",
                    "Control In","Control In","Control In","Blank","Blank","Blank",
                    "QC","QC","QC","QC","QC","QC","QC","QC","QC","QC"
                    ],
    'Bacterial Species':["A","A","A","A","A","A","B","B","B","B","B","B","C","C",
                         "C","C","C","C","NA","NA","NA","NA","NA","NA","NA","NA",
                         "NA","NA","NA","NA","NA","NA","NA","NA","NA","NA","NA"
                         ],
    'Metabolome Type':["Extracellular","Extracellular","Extracellular","Intracellular",
                       "Intracellular","Intracellular","Extracellular","Extracellular",
                       "Extracellular","Intracellular","Intracellular","Intracellular",
                       "Extracellular","Extracellular","Extracellular","Intracellular",
                       "Intracellular","Intracellular","Extracellular","Extracellular",
                       "Extracellular","Intracellular","Intracellular","Intracellular",
                       "NA","NA","NA","NA","NA","NA","NA","NA","NA","NA","NA","NA","NA"
                       ],

    })

#TODO: Update with third report's own methods
layout = dbc.Container([
    dcc.Link("Go back to view other reports", href=accountIndexPage),
    html.Br(),
    html.H5("{}".format(page_name), style={'textAlign': 'center'}),
    html.Br(),
    html.H4("Experimental Details", 
            style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Card(
            dbc.CardBody(
                dcc.Markdown('''
                             **Sampling:** 
                             
                             - Each bacterial species grown into the exponential growth phase
                             
                             - Aliquot centrifuged to separate pellet and supernatant for intracellular and extracellular metabolomics analyses respectively
                             
                             - Bacterial samples frozen at -70 °C 
                             
                             - All samples underwent chloroform:methanol:water (1:3:1) extraction
                             
                             - Metabolite samples frozen at -80 °C until analysis
                             

                             ''')
    ))
    ]),
    html.Br(),
    html.H5("Sample Details", style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(data = dataset_info.to_dict('records'), 
                                 columns=[{'id': c, 'name': c} for c in dataset_info.columns],
                                 style_cell = { 
                                     "font_family":"sans-serif"
                                     }
                                 ),
            ], 
            )
        ]),
    html.Br(),
    html.H4("Data Acquisition and Analysis", 
            style={'textAlign': 'center'}),
    #Add standard RHIMMS method details into the report information
    html.Div(StandardRHIMMSMethodText()),
    html.Br(),
    html.H4("Data processing procedures for statistical analysis", 
            style={'textAlign': 'center'}),
    #Add standard data processing description into the report information
    html.Div(StandardStatProcessingText()),
])
                    
