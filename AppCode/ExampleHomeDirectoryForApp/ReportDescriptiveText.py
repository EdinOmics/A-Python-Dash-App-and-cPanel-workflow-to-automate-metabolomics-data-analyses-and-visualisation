#Script contains set blocks of text used for the Metabolomics Reports
#Author: Jessica M. O'Loughlin
#Contact: J.O'Loughlin@sms.ed.ac.uk
#Manager: Dr Tessa Moses
#Created: 29/09/2025

from dash import html, dcc
import dash_bootstrap_components as dbc

#Standard RHIMMS Method
#Last changed: 29/09/2025
def StandardRHIMMSMethodText():
    return html.Div([
        dbc.Row([
            dbc.Card(
                dbc.CardBody(
                    dcc.Markdown('''
        Data was acquired using the EdinOmics in-house rapid HILIC-Z Ion Mobility Mass Spectrometry (RHIMMS reference) method. RHIMMS uses a rapid (under 5 minutes per sample) liquid chromatography separation followed by a second separation of metabolites in the drift tube (based on metabolite structure cross section) to allow high confidence in identification. This method allows economical high-throughput analysis of compounds using liquid chromatography and mass spectrometry in large sample sets. 
        
        Data was acquired in positive and negative ionisation modes on an Agilent 1290 Infinity II series UHPLC system hyphenated with an Agilent 6560 ion mobility quadrupole time-of-flight instrument. Experimental samples were blocked and randomised to minimise the impact of measurement error. Pooled quality control samples obtained from the experimental samples were collected after every 5 experimental sample injections to monitor the instrument state throughout data acquisition. The raw data was processed using the Agilent MassHunter software suite and underwent:     
                                             
        - Demultiplexing (PNNL PreProcessor v2020.03.23)             
        
        - Accurate Mass Calibration (AgtTofReprocessUI 10.0)     
        
        - Drift Time Calibration (IM-MS Browser 10.0)
        
        - Feature Extraction (Mass Profiler 10.0)
        
        - High Resolution Demultiplexing (HRdm v41)
        
        - Final Feature Extraction (Mass Profiler 10.0)
        
        - Annotation using accurate mass and CCS values against selected personal compound databases (PCDLs) and libraries
            
        Where multiple features were assigned the same metabolite annotation, one of each annotation was selected based on:
                                            
        - The frequency of samples it was present in
        
        - The availability of Collision Cross Section (CCS) data
        
        - Its average intensity
        
        - Its ion type (preferring \[M+H\]+ , \[M-H\]-, or \[M+Na\]+ ions)
        
        Reference to RHIMMS: Pičmanová M, Moses T, Cortada-Garcia J, Barrett G, Florance H, Pandor S, Burgess K. Rapid HILIC-Z ion mobility mass spectrometry (RHIMMS) method for untargeted metabolomics of complex biological samples. Metabolomics. 2022;18(3):16. doi: 10.1007/s11306-022-01871-1.
        ''')
        ))
        ])
        ])

#Standard Data processing decription for methods pages
#Last changed: 29/09/2025
def StandardStatProcessingText():
    return html.Div([
        dbc.Row([
            dbc.Card(
                dbc.CardBody(
                    dcc.Markdown('''
        To increase the reliability of statistical analysis, the data underwent a Log10 transformation as well as mean-centre and Pareto scaling (dividing the metabolite intensities for each sample by the square root for their standard deviation) to give the frequency of metabolite intensities a normal/Gaussian distribution. This can be visualised in the "Raw Data" and "Normalised Data" pages.     
        ''')
        ))
        ]),
        ])
