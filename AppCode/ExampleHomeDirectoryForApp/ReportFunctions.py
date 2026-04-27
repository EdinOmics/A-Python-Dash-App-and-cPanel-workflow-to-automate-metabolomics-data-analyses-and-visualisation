#Script contains functions required for the Metabolomics Reports
#Author: Jessica M. O'Loughlin
#Contact: J.O'Loughlin@sms.ed.ac.uk
#Manager: Dr Tessa Moses
#Created: 04/08/2025

from dash import dash_table
import pandas as pd
import plotly.express as px
import numpy as np
import math
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from sklearn.preprocessing import MinMaxScaler
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from scipy import stats

#Subset data frame + save in memory storage
#Last updated: 04/08/2025 (Jessica O'Loughlin)
def update_data(n_clicks, value_label, value_sample, mainDataset):
    
    if n_clicks is None:
        raise PreventUpdate
    #Only update data once user has selected it
    else:
        #Read raw metabolomics data
        df_sel = pd.read_csv(mainDataset)

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
        
        #Only keep selected Samples/Labels
        df_sel = df_sel[df_sel['Label'].isin(list(value_label))]
        df_sel = df_sel[df_sel['Sample'].isin(list(value_sample))]
        
        df_raw_transposed = df_sel.copy()
        #Filtering Dataframe rows in the non-normalised data
        #Therefore: both have the same selected user data 
        df_raw_transposed = df_raw_transposed[df_raw_transposed.Sample.isin(df_sel.Sample)]
        
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

    #Return data as dataframes (will be returned as list of dictionaries within the report script)
    return df_sel, df_raw_transposed, pca_metabolite_list, plsda_metabolite_list

#Display raw data table
#Last updated: 04/08/2025 (Jessica O'Loughlin)
def update_raw_table(data):
    
    if data is None:
        raise PreventUpdate
    else:
        dff = pd.DataFrame(data)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        str_variables = set(dff.select_dtypes("object" or "str").columns)
        
        #Get a list of column headers
        column_list = list(dff.columns)
        #Automatically generate list of metabolites
        
        #Remove the str_variables to get metabolites only
        metabolite_list = [metabolite for metabolite in 
                           column_list if metabolite not in list(str_variables)]
     
        #Table format
        overview_table = dash_table.DataTable(
                    #id = "datatable-interactivity",
                    data = dff.to_dict("records"), 
                    sort_action  = "native",
                    columns = [{
                        "id":c, 
                        "name":c, 
                        "selectable":True
                        } for c in dff.columns], 
                    fixed_rows = {"headers":True}, 
                    editable = False,
                    style_table = {"minWidth":"100%", "overflowX":"auto"},
                    style_cell = {
                        "minWidth":200, "maxWidth":200, "width":200, 
                        "height":"auto", "whiteSpace":"inherit",
                        "textAlign":"left", "padding":"1px", 
                        "font_size":"15px", "font_family":"sans-serif" 
                    }, 
                    #fixed_columns = {"headers":True, "data":1},
                    style_header = {
                        "backgroundColor":"rgb(230, 230, 230)",
                        "fontWeight":"bold", 
                        "border":"1px solid black"
                    }, 
                    style_data_conditional = [ #Alternate row colouring
                        {
                            "if":{"row_index":"odd"}, 
                            "backgroundColor":"rgb(248, 248, 248)"
                        }
                    ],
                )
        
        #Put data into long data format for histogram
        dff = pd.melt(dff, id_vars='Sample', value_vars=metabolite_list)
    
        dff.rename(columns={'variable':'Metabolites', 'value':'PeakIntensity_raw'}, inplace=True)
        
        #Plot histogram
        hist_raw = px.histogram(dff, x="PeakIntensity_raw", 
                                labels={'PeakIntensity_raw': "Feature",
                                        "count": "Frequency"})
        
        #Delete intermediate objects (save memory space)
        del [dff, str_variables, column_list, metabolite_list]
    
    return overview_table, hist_raw


#Display normalised data table
#Last updated: 04/08/2025 (Jessica O'Loughlin)
def update_normalised_table(data):
    if data is None:
        raise PreventUpdate
    else:
        dff = pd.DataFrame(data)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        str_variables = set(dff.select_dtypes("object" or "str").columns)
        
        #Get a list of column headers
        column_list = list(dff.columns)
        #Automatically generate list of metabolites
        
        #Remove the str_variables to get metabolites only
        metabolite_list = [metabolite for metabolite in 
                           column_list if metabolite not in list(str_variables)]
    
        #Table format
        overview_table = dash_table.DataTable(
                    #id = "datatable-interactivity",
                    data = dff.to_dict("records"), 
                    sort_action  = "native",
                    columns = [{
                        "id":c, 
                        "name":c, 
                        "selectable":True
                        } for c in dff.columns], 
                    fixed_rows = {"headers":True}, 
                    editable = False,
                    style_table = {"minWidth":"100%", "overflowX":"auto"},
                    style_cell = {
                        "minWidth":200, "maxWidth":200, "width":200, 
                        "height":"auto", "whiteSpace":"inherit",
                        "textAlign":"left", "padding":"1px", 
                        "font_size":"15px", "font_family":"sans-serif" 
                    }, 
                    #fixed_columns = {"headers":True, "data":1},
                    style_header = {
                        "backgroundColor":"rgb(230, 230, 230)",
                        "fontWeight":"bold", 
                        "border":"1px solid black"
                    }, 
                    style_data_conditional = [ #Alternate row colouring
                        {
                            "if":{"row_index":"odd"}, 
                            "backgroundColor":"rgb(248, 248, 248)"
                        }
                    ],
                )
        
        #Put data into long data format for histogram
        dff = pd.melt(dff, id_vars='Sample', value_vars=metabolite_list)
    
        dff.rename(columns={'variable':'Metabolites', 'value':'PeakIntensity_norm'}, inplace=True)
        
        #Plot histogram
        hist_norm = px.histogram(dff, x="PeakIntensity_norm", 
                                labels={'PeakIntensity_norm': "Feature",
                                        "count": "Frequency"})
    
        #Delete intermediate objects (save memory space)
        del [dff, str_variables, column_list, metabolite_list]
    
    return overview_table, hist_norm

#Interactive PCA plots (including PCA VIP and Heat Map)
#Keep groups in the user-specified order
#Last updated: 29/10/2025 (Jessica O'Loughlin)
def update_pca_UserGroupOrder(data, value_label):
    
    if data is None:
        raise PreventUpdate
    else:

        pca_df_str = pd.DataFrame(data)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        str_variables = set(pca_df_str.select_dtypes("object" or "str").columns)
        
        #Generate list of metabolites
        #Remove the str_variables to get metabolites only
        metabolite_list = [metabolite for metabolite in 
                           list(pca_df_str.columns) if metabolite not in list(str_variables)]
        
        #Only keep numerical variables (remove strings)
        pca_df = pca_df_str.drop(str_variables, axis = 1)
        pca_df = pca_df.apply(pd.to_numeric, errors='coerce', axis=1)
        
        #2D plot
        pca_2D = PCA(n_components=3)
        components_2D = pca_2D.fit_transform(pca_df)
        
        #Calculate the individual PC and total variation 
        total_var_pca_2D = pca_2D.explained_variance_ratio_.sum() * 100
        axis_1_var_pca_2D = pca_2D.explained_variance_ratio_[0] * 100
        axis_2_var_pca_2D = pca_2D.explained_variance_ratio_[1] * 100
        
        components_2D = pd.DataFrame(components_2D)
        
        #Concatenate the PCA outputs and the sample/label IDs together
        components_2D = pd.concat([components_2D.reset_index(drop = True), 
                                            pca_df_str], 
                                           axis = 1)
        components_2D = components_2D.rename({0: 'PCA_Axis_1', 1: 'PCA_Axis_2'}, axis=1)
        components_2D = components_2D[["PCA_Axis_1", "PCA_Axis_2", "Sample", "Label"]]

        #Plot the 2D PCA plot (non-selectable)
        pca_scores_plot = px.scatter(components_2D, x='PCA_Axis_1', 
                                     y='PCA_Axis_2',
                                     color=components_2D['Label'],
                                     hover_data = "Sample",
                                     color_discrete_sequence=px.colors.qualitative.Light24
                                     )
        
        #Get list of colours + assign to each group
        total_colours = px.colors.qualitative.Light24 + px.colors.qualitative.Light24 + px.colors.qualitative.Light24
        total_colours = total_colours[0:len(components_2D["Label"].unique())]
        total_colours = {'Label':components_2D["Label"].unique(), 
                'colour':total_colours}
        
        total_colours = pd.DataFrame(total_colours)
        
        #Calculate 95% confidence intervals for each group + add onto the PCA Scores plot
        for index, row in total_colours.iterrows(): 
            values = components_2D.loc[components_2D['Label'] == row['Label']]
            
            var_matrix = values[["PCA_Axis_1", "PCA_Axis_2"]]
            
            level=0.95 #0.95 = 95% confience interval
            npoints=25 #default 100
            
            #Added the randomisation seed to make ellipses consistent between identical runs
            np.random.seed(seed=5)
            t = np.sqrt(np.quantile(np.random.chisquare(2, size=10000), level))
            
            #Set centre point for the ellipses
            centre = var_matrix.mean(axis=0)
            
            #Calculate the covariance
            x = np.cov(var_matrix, rowvar=0)
            x = x.flatten().tolist()
            r = x[1] #Covariance
            xind = x[0] #PC1 variance
            yind = x[3] #PC2 variance
            
            scale_x = np.sqrt(xind)
            scale_y = np.sqrt(yind)
            if scale_x > 0:
                r = r / scale_x
            if scale_y > 0:
                r = r / scale_y
                
            d = np.arccos(r)
            a = np.linspace(0, 2 * np.pi, num=npoints)
            results = np.column_stack((t * scale_x * np.cos(a + d / 2) + centre.iloc[0],
                                       t * scale_y * np.cos(a - d / 2) + centre.iloc[1]))
            
            # Convert numpy array to DataFrame
            results = pd.DataFrame(results, columns=['PCA_Axis_1', 'PCA_Axis_2'])

            # Create a plotly express line plot with filled area
            ellipsis_fig = px.line(results, x='PCA_Axis_1', y='PCA_Axis_2', 
                          markers=False, #Was True
                          line_shape='spline'
                          )

            # Update traces to fill the area beneath the line
            ellipsis_fig.update_traces(fill='toself', 
                              fillcolor=row['colour'], 
                              line_color=row['colour'], 
                              opacity=0.3)
            
            # pca_scores_plot = go.Figure(data = pca_scores_plot.data + ellipsis_fig.data)
            pca_scores_plot = go.Figure(data = ellipsis_fig.data + pca_scores_plot.data)
            pca_scores_plot.update_layout(
                title=dict(text=f'Total Explained Variance: {total_var_pca_2D:.2f}%'),
                xaxis=dict(title=dict(text=f"PC 1 ({axis_1_var_pca_2D:.2f}%)")),
                yaxis=dict(title=dict(text=f"PC 2 ({axis_2_var_pca_2D:.2f}%)")),
                legend=dict(title=dict(text="Label"))
                )
        
        #Save Loadings axis 1 as a data frame
        loadings = pd.DataFrame(pca_2D.components_[0])
        #Rename column
        loadings = loadings.rename(columns = {0:"Loadings 1"})
        #Add Loadings axis 2 to the dataframe
        loadings["Loadings 2"] = list(pca_2D.components_[1])
        #Add the metabolite list to the loadings data
        loadings["Metabolite"] = metabolite_list 
        
        # Change pcs components ndarray to a dataframe
        importance_df = pd.DataFrame(pca_2D.components_)
        # Assign columns
        importance_df.columns = pca_df.columns
        # Change to absolute values
        importance_df =importance_df.apply(np.abs)
        # Transpose
        importance_df=importance_df.transpose()
        # Change column names again
        ## First get number of pcs
        num_pcs = importance_df.shape[1]
        ## Generate the new column names
        new_columns = [f'PC{i} VIP score' for i in range(1, num_pcs + 1)]
        ## Now rename
        importance_df.columns = new_columns
        #Multiply VIP score values by 10
        importance_df = importance_df.apply(lambda x: x*10)
        
        #PCA axis 1 top 50 important features
        pca_top_50_features = importance_df['PC1 VIP score'].sort_values(ascending = False)[:50]
        pca_top_50_features = pca_top_50_features.reset_index()
        pca_top_50_features = pca_top_50_features.rename(columns = {"index":"Metabolites"})
        
        #Create list of the top 50 metabolites
        top_metabolites_list = list(pca_top_50_features["Metabolites"])
        
        df_toscale = pca_df_str.set_index('Sample')
        #Remove Sample info + set Label column as the index
        df_toscale = df_toscale.set_index('Label')
        
        #Scale each column (metabolite) individually
        scaler = MinMaxScaler()
        scaled_df = pd.DataFrame(scaler.fit_transform(df_toscale), 
                                 columns=df_toscale.columns)
        scaled_df.index = list(df_toscale.index)
        
        ### Heatmap for Label averages ###
        #Calculate the average scaled peak intensities by Label (group)
        #Where the label is the index
        label_groups = scaled_df.groupby(scaled_df.index)
        mean_scaled_df = label_groups.mean()
        #Only keep the top 50 metabolites
        mean_scaled_df = mean_scaled_df[top_metabolites_list]
        #Transpose the dataframe (show metabolites as rows)
        mean_scaled_df = mean_scaled_df.transpose()
    
        pca_loadings_plot = px.scatter(loadings, x="Loadings 1", y="Loadings 2", 
                         color="Metabolite",
                         color_discrete_sequence=px.colors.qualitative.Light24, 
                         custom_data = ["Metabolite"]
                        )
        #Remove legend (metabolites can be viewed by hovering over the datapoints)
        pca_loadings_plot.update_layout(showlegend=False)
        
        #Plot VIP scores
        vip_plot_pca = px.scatter(pca_top_50_features, 
                          x = "PC1 VIP score", 
                          y = "Metabolites", 
                          #Specify metabolite order
                          # --> prevents random metabolites being added
                          category_orders = {"Metabolites":list(pca_top_50_features["Metabolites"])})
        vip_plot_pca.layout.width = 500
        vip_plot_pca.layout.height = 900
        vip_plot_pca.update_yaxes(tickmode = 'linear') #Displays all categories
        #Add significance threshold line onto VIP plot
        vip_plot_pca.add_vline(x=1.0, line_width=3, line_dash="dash", line_color="red")
        
        #Change the order of the columns (i.e. sample groups) to the user selection
        mean_scaled_df = mean_scaled_df[value_label]

        #Plot averages heat map
        heatmap_mean_pca = px.imshow(mean_scaled_df, aspect = 'auto', 
                                 color_continuous_scale='Blues')
        heatmap_mean_pca.update_layout(
                margin={"t": 0, "b": 0, "r": 0, "l": 0, "pad": 0}
                )
        heatmap_mean_pca.layout.height = 800
        heatmap_mean_pca.layout.width = 610
        heatmap_mean_pca.layout.yaxis.type = 'category'
        heatmap_mean_pca.update_xaxes(tickmode = 'linear')
        heatmap_mean_pca.update_yaxes(tickmode = 'linear')
        #Remove y-axis labels (optional)
        #heatmap_mean.update_yaxes(visible=False, showticklabels=False)
        
        #Delete intermediate objects (save memory space)
        del [pca_df_str, str_variables, metabolite_list, pca_df, pca_2D, components_2D, 
             total_var_pca_2D, axis_1_var_pca_2D, axis_2_var_pca_2D, total_colours,
             loadings, importance_df, num_pcs, new_columns, pca_top_50_features,
             top_metabolites_list, df_toscale, scaled_df, scaler, label_groups, mean_scaled_df]
    
    return pca_scores_plot, pca_loadings_plot, vip_plot_pca, heatmap_mean_pca

#Select metabolite from loadings plot
#Keep user-defined group order
#Last updated: 29/10/2025 (Jessica O'Loughlin)
def update_average_plots_pca_UserGroupOrder(clickData, df_raw_T, df_norm, value_label):
    if clickData is None:
        raise PreventUpdate
    else:
        metabolite_name = str(clickData['points'][0]['customdata'][0]) 
        
        ### Average calculations on the transposed, raw data ###
        df_raw_T = pd.DataFrame(df_raw_T)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        #Create list of columns names with str_variables + metabolite of interest
        columns_keep = set(df_raw_T.select_dtypes("object" or "str").columns)
        columns_keep.add(metabolite_name)
    
        #Create new df subset with data in columns_keep
        df_raw_T = df_raw_T[list(columns_keep)]
    
        #Calculate the average and standard deviations by Label group 
        df_average = pd.DataFrame(df_raw_T.groupby("Label")[metabolite_name].mean()).reset_index()
        df_average = df_average.rename(columns = {metabolite_name:"Mean"})
        
        df_stdev = pd.DataFrame(df_raw_T.groupby("Label")[metabolite_name].std()).reset_index()
        df_stdev = df_stdev.rename(columns = {metabolite_name:"STDEV"})
        
        #Merge the average and stdev results 
        df_graph = pd.concat([df_average, df_stdev["STDEV"]], axis = 1)
    
        fig_raw_pca = go.Figure()
        fig_raw_pca.add_trace(go.Bar(
            x=list(df_graph["Label"]),
            y=list(df_graph["Mean"]),
            error_y=dict(type='data', array=list(df_graph["STDEV"]))
        ))
        fig_raw_pca.update_layout(title_text=metabolite_name, title_x=0.5, 
                         xaxis_title="Sample group", 
                         yaxis_title="Average Peak Intensity") 
        fig_raw_pca.update_xaxes(categoryorder='array', categoryarray = value_label)
        
        ### Average calculations on the normalised data ###
        df_norm = pd.DataFrame(df_norm)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        #Create list of columns names with str_variables + metabolite of interest
        columns_keep_norm = set(df_norm.select_dtypes("object" or "str").columns)
        columns_keep_norm.add(metabolite_name)
    
        #Create new df subset with data in columns_keep
        df_norm = df_norm[list(columns_keep_norm)]
    
        #Calculate the average and standard deviations by Label group 
        df_average_norm = pd.DataFrame(df_norm.groupby("Label")[metabolite_name].mean()).reset_index()
        df_average_norm = df_average_norm.rename(columns = {metabolite_name:"Mean"})
        
        df_stdev_norm = pd.DataFrame(df_norm.groupby("Label")[metabolite_name].std()).reset_index()
        df_stdev_norm = df_stdev_norm.rename(columns = {metabolite_name:"STDEV"})
        
        #Merge the average and stdev results 
        df_graph_norm = pd.concat([df_average_norm, df_stdev_norm["STDEV"]], axis = 1)
    
        fig_norm_pca = go.Figure()
        fig_norm_pca.add_trace(go.Bar(
            x=list(df_graph_norm["Label"]),
            y=list(df_graph_norm["Mean"]),
            error_y=dict(type='data', array=list(df_graph_norm["STDEV"]))
        ))
        fig_norm_pca.update_layout(title_text=metabolite_name, title_x=0.5, 
                         xaxis_title="Sample group", 
                         yaxis_title="Average Peak Intensity")
        fig_norm_pca.update_xaxes(categoryorder='array', categoryarray = value_label)
        
        #Delete intermediate objects (save memory space)
        del [metabolite_name, df_raw_T, columns_keep, df_average, df_stdev, 
             df_graph, df_norm, columns_keep_norm, df_average_norm, df_graph_norm]

    return fig_raw_pca, fig_norm_pca

#Update metabolite selection plots (PCA tab)
#Keep user-defined group order
#Last updated: 29/10/2025 (Jessica O'Loughlin)
def pca_any_metab_plots_UserGroupOrder(n_clicks, data_raw, data_norm, rawplot_type, rawplot_axis, normplot_type, metabolite_name, value_label):
    if n_clicks is None:
        raise PreventUpdate
    else:
        metabolite_name = list(metabolite_name)
        
        data_raw = pd.DataFrame(data_raw)
        data_norm = pd.DataFrame(data_norm)

        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        #Create list of columns names with str_variables + metabolite of interest
        columns_keep = set(data_raw.select_dtypes("object" or "str").columns)
        columns_keep = columns_keep.union(metabolite_name)
        
        ## Average bar plots (raw data)
        #Create new df subset with data in columns_keep
        df_average_pre = data_raw[list(columns_keep)]
        #Convert to long data format
        df_average_pre = pd.melt(df_average_pre, 
                                 id_vars = 'Label',
                                 var_name='Metabolites',
                                 value_name='Intensities',
                                 value_vars=list(metabolite_name))
        
        #Calculate the average and standard deviations by Label group 
        df_average = pd.DataFrame(df_average_pre.groupby(["Label", "Metabolites"]).mean()).reset_index()
        df_average = df_average.rename(columns = {"Intensities":"Mean"})
        
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
                                                   categoryarray=value_label)
                
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
                pca_any_metab_raw_fig.update_xaxes(categoryorder='array', 
                                                   categoryarray=value_label)
        
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
                                                   'Label':value_label}, 
                                labels={"Intensities": "Raw Intensities"},
                                )
            else:
                pca_any_metab_raw_fig = px.box(df_box, 
                                x = 'Label', 
                                y = 'Intensities', 
                                color = 'Metabolites', 
                                category_orders = {'Metabolites':list(metabolite_name), 
                                                   'Label':value_label},
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
                                                    'Label':value_label}, 
                                labels={"Intensities": "Raw Intensities"},
                                )
            else:
                pca_any_metab_raw_fig = px.violin(df_violin, 
                                x = 'Label', 
                                y = 'Intensities', 
                                color = 'Metabolites',
                                category_orders = {'Metabolites':list(metabolite_name), 
                                                   'Label':value_label},
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
            pca_any_metab_norm_fig.update_xaxes(categoryorder='array', 
                                                categoryarray=value_label)
                
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
                                               'Label':value_label}, 
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
                                               'Label':value_label}, 
                            labels={"Intensities": "Normalised Intensities"},
                            )
            
        del [metabolite_name, data_raw, data_norm, columns_keep, df_average_pre, 
             rawplot_type, df_stdev, df_average, df_graph, df_average_pre_norm]
        
    return pca_any_metab_raw_fig, pca_any_metab_norm_fig


#Interactive PLS-DA plots
#Last updated: 04/08/2025 (Jessica O'Loughlin)
def update_plsda_UserGroupOrder(data, value_label):
    if data is None:
        raise PreventUpdate
    else:
    
        dff = pd.DataFrame(data)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        str_variables = set(dff.select_dtypes("object" or "str").columns)
        

        #Automatically generate list of metabolites
        #Remove the str_variables to get metabolites only
        metabolite_list = [metabolite for metabolite in 
                           list(dff.columns) if metabolite not in list(str_variables)]
        
        plsda_df = dff.copy()
        
        #Get number of data rows (excluding row containing metabolite names)
        comp_num = len(plsda_df)-1
        
        #Get cls dataframe
        cls_data = plsda_df[['Label']]
        variance_to_SS_factor = len(cls_data)

        # Convert categorical data to numerical data using cat.codes
        cls_data['Label'] = cls_data['Label'].astype('category')
        cls_data['x_codes'] = cls_data['Label'].cat.codes
        cls_data['x_codes'] = cls_data['x_codes']+1
        
        #R's base scale() function translated into Python
        def scale_default(x, center=True, scale=True):
            x = np.asarray(x)  # Make sure x is a NumPy array
            if x.ndim == 1:
                x = x.reshape(-1, 1)  # Work with 2D array for consistency
            
            nc = x.shape[1]

            # Centering the data
            if isinstance(center, bool):
                if center:
                    center = np.nanmean(x, axis=0)  # Compute mean considering NaN
                    x = x - center
            elif isinstance(center, (list, np.ndarray)):
                if len(center) != nc:
                    raise ValueError("length of 'center' must equal the number of columns of 'x'")
                x = x - center
            else:
                raise ValueError("center must be either a boolean or a numeric array")

            # Scaling the data
            if isinstance(scale, bool):
                if scale:
                    scale = np.sqrt(np.nansum(x**2, axis=0) / np.maximum(1, np.sum(~np.isnan(x), axis=0) - 1))
                    x = x / scale
            elif isinstance(scale, (list, np.ndarray)):
                if len(scale) != nc:
                    raise ValueError("length of 'scale' must equal the number of columns of 'x'")
                x = x / scale
            else:
                raise ValueError("scale must be either a boolean or a numeric array")

            return x

        cls_scaled = scale_default(cls_data['x_codes'], center = True, scale = True)
        
        #Remove the string variables
        plsda_df = plsda_df.drop(str_variables, axis = 1)
        
        #Fit the PLS-DA regression model
        pls = PLSRegression(n_components=comp_num, scale=False) # (1)
        pls.fit(plsda_df, cls_scaled) # (2)
        
        ##PLSDA Scores and Loadings plot calculations
        #Calculate the PLS-DA variance for each axis after the model has been fit
        #Multiply by variance_to_SS_factor to convert variance to Sums of Squares
        variance_in_x = np.var(pls.x_scores_, axis = 0)*variance_to_SS_factor

        #Create variables for the axes of the plots with their respective variances
        axis_1_var_plsda_2D = round((variance_in_x[0]/sum(variance_in_x))*100, 1)
        axis_2_var_plsda_2D = round((variance_in_x[1]/sum(variance_in_x))*100, 1)
        #Calculate the total variance explained by the displayed axes (2D)
        total_var_plsda_2D = round(axis_1_var_plsda_2D + axis_2_var_plsda_2D, 1)
        
        #Create a data frame with the PLS-DA score results
        scores = pd.DataFrame(pls.x_scores_)
        scores = scores.rename(columns = {0:"Component 1", 1:"Component 2",
                                          2:"Component 3", 3:"Component 4",
                                          4:"Component 5", 5:"Component 6",
                                          6:"Component 7", 7:"Component 8",})

        #Add the sample and metabolite information from the main data frame
        scores = pd.concat([scores.reset_index(drop = True), 
                                   dff], 
                                  axis = 1)
        scores = scores[["Component 1", "Component 2", "Sample", "Label"]]
        
        #Plot PLS-DA scores
        interactive_plsda_plot_2D = px.scatter(
            scores, 
            x="Component 1", 
            y="Component 2", 
            color=scores['Label'],
            hover_data = ['Sample'],
            color_discrete_sequence=px.colors.qualitative.Light24
            )
        
        total_colours = px.colors.qualitative.Light24 + px.colors.qualitative.Light24 + px.colors.qualitative.Light24
        
        total_colours = total_colours[0:len(scores["Label"].unique())]

        total_colours = {'Label':scores["Label"].unique(), 
                'colour':total_colours}
        
        
        total_colours = pd.DataFrame(total_colours)
        
        for index, row in total_colours.iterrows(): 
            values = scores.loc[scores['Label'] == row['Label']]
            
            var_matrix = values[["Component 1", "Component 2"]]
            
            level=0.95 #0.95 = 95% confience interval
            npoints=25 #default 100
            
            #Added the randomisation seed to make ellipses consistent between identical runs
            np.random.seed(seed=5)
            t = np.sqrt(np.quantile(np.random.chisquare(2, size=10000), level))
            
            #Set centre point for the ellipses
            centre = var_matrix.mean(axis=0)
            
            #Calculate the covariance
            x = np.cov(var_matrix, rowvar=0)
            x = x.flatten().tolist()
            r = x[1] #Covariance
            xind = x[0] #PC1 variance
            yind = x[3] #PC2 variance
            
            scale_x = np.sqrt(xind)
            scale_y = np.sqrt(yind)
            if scale_x > 0:
                r = r / scale_x
            if scale_y > 0:
                r = r / scale_y
                
            d = np.arccos(r)
            a = np.linspace(0, 2 * np.pi, num=npoints)
            results = np.column_stack((t * scale_x * np.cos(a + d / 2) + centre.iloc[0],
                                       t * scale_y * np.cos(a - d / 2) + centre.iloc[1]))
            
            # Convert numpy array to DataFrame
            results = pd.DataFrame(results, columns=['Component 1', 'Component 2'])

            # Create a plotly express line plot with filled area
            ellipsis_fig = px.line(results, x='Component 1', y='Component 2', 
                          markers=False, #Was True
                          line_shape='spline'
                          )

            # Update traces to fill the area beneath the line
            ellipsis_fig.update_traces(fill='toself', 
                              fillcolor=row['colour'], 
                              line_color=row['colour'], 
                              opacity=0.3)
            
            # pca_scores_plot = go.Figure(data = pca_scores_plot.data + ellipsis_fig.data)
            interactive_plsda_plot_2D = go.Figure(data = ellipsis_fig.data + interactive_plsda_plot_2D.data)
            interactive_plsda_plot_2D.update_layout(
                title=dict(text=f"Total Explained Variance: {total_var_plsda_2D:.2f}%"),
                xaxis=dict(title=dict(text=f"Component 1 ({axis_1_var_plsda_2D:.2f}%)")),
                yaxis=dict(title=dict(text=f"Component 2 ({axis_2_var_plsda_2D:.2f}%)")),
                legend=dict(title=dict(text="Label"))
                )
        
        ##VIP score calculations
        # Change pcs components ndarray to a dataframe
        importance_df = pd.DataFrame(pls.x_rotations_)
        importance_df = importance_df.transpose()
    
        # Assign columns
        importance_df.columns  = plsda_df.columns
        #importance_df = importance_df.drop("num_cat", axis = 1)
        # Change to absolute values
        importance_df =importance_df.apply(np.abs)
        # Transpose
        importance_df=importance_df.transpose()
        # Change column names again
        # First get number of pcs
        num_pcs = importance_df.shape[1]
        ## Generate the new column names
        new_columns = [f'PLSDA{i} VIP score' for i in range(1, num_pcs + 1)]
        ## Now rename
        importance_df.columns = new_columns 
        #Multiply VIP score values by 10
        importance_df = importance_df.apply(lambda x: x*10)
        #PLSDA axis 1 top 50 important features
        pls1_top_50_features = importance_df['PLSDA1 VIP score'].sort_values(ascending = False)[:50]
        pls1_top_50_features = pls1_top_50_features.reset_index()
        pls1_top_50_features = pls1_top_50_features.rename(columns = {"index":"Metabolites"})
        
        #Create list of the top 50 metabolites
        top_metabolites_list = list(pls1_top_50_features["Metabolites"])
        
        dff = dff.set_index('Sample')
        #Remove Sample info + set Label column as the index
        dff = dff.set_index('Label')
        
        ##Generate heat map with top 50 metabolites from VIP calcs
        #Scale each column (metabolite) individually
        scaler = MinMaxScaler()
        scaled_df = pd.DataFrame(scaler.fit_transform(dff), columns=dff.columns)
        scaled_df.index = list(dff.index)
        
        ### Heatmap for Label averages ###
        #Calculate the average scaled peak intensities by Label (group)
        #Where the label is the index
        label_groups = scaled_df.groupby(scaled_df.index)
        mean_scaled_df = label_groups.mean()
        #Only keep the top 50 metabolites
        mean_scaled_df = mean_scaled_df[top_metabolites_list]
        #Transpose the dataframe (show metabolites as rows)
        mean_scaled_df = mean_scaled_df.transpose()
        
        loadings = pd.DataFrame(pls.x_weights_)
        loadings = loadings.rename(columns = {0:"Loadings 1", 1:"Loadings 2",
                                             2:"Loadings 3", 3:"Loadings 4",
                                             4:"Loadings 5", 5:"Loadings 6",
                                             6:"Loadings 7", 7:"Loadings 8",})
        #Add the metabolite list to the loadings data
        loadings["Metabolite"] = metabolite_list 
        
        #Plot PLS-DA loadings
        plsda_loadings_plot = px.scatter(
            loadings, x="Loadings 1", y="Loadings 2",   
            color='Metabolite',
            color_discrete_sequence=px.colors.qualitative.Light24, 
            custom_data = ["Metabolite"]
        )
        plsda_loadings_plot.update_layout(showlegend=False)
        
        #Plot VIP scores
        vip_plot_plsda = px.scatter(pls1_top_50_features, 
                              x = "PLSDA1 VIP score", 
                              y = "Metabolites", 
                              #Specify metabolite order
                              # --> prevents random metabolites being added
                              category_orders = {"Metabolites":list(pls1_top_50_features["Metabolites"])})
        vip_plot_plsda.layout.width = 500
        vip_plot_plsda.layout.height = 900
        vip_plot_plsda.update_yaxes(tickmode = 'linear') #Displays all categories
        #Add significance threshold line onto VIP plot
        vip_plot_plsda.add_vline(x=1.0, line_width=3, line_dash="dash", line_color="red")
        
        #Change the order of the columns (i.e. sample groups) to the user selection
        mean_scaled_df = mean_scaled_df[value_label]
        
        #Plot group-average heat map
        heatmap_mean_plsda = px.imshow(mean_scaled_df, aspect = 'auto', 
                                 color_continuous_scale='Blues')
        heatmap_mean_plsda.update_layout(
                margin={"t": 0, "b": 0, "r": 0, "l": 0, "pad": 0}
                )
        heatmap_mean_plsda.layout.height = 800
        heatmap_mean_plsda.layout.width = 700
        heatmap_mean_plsda.layout.yaxis.type = 'category'
        heatmap_mean_plsda.update_xaxes(tickmode = 'linear')
        heatmap_mean_plsda.update_yaxes(tickmode = 'linear')
        #Remove y-axis labels (optional)
        #heatmap_mean_plsda.update_yaxes(visible=False, showticklabels=False)
        
        #Delete intermediate object (save memory space)
        del [dff, str_variables, metabolite_list, plsda_df, comp_num, cls_data,
             scale_default, x, cls_scaled, pls,
             variance_in_x, total_var_plsda_2D, axis_1_var_plsda_2D, 
             axis_2_var_plsda_2D, scores, total_colours, values, var_matrix, 
             importance_df, num_pcs, new_columns, pls1_top_50_features, 
             top_metabolites_list, scaler, scaled_df, label_groups, 
             mean_scaled_df, loadings]
    
    return interactive_plsda_plot_2D, plsda_loadings_plot, vip_plot_plsda, heatmap_mean_plsda

#Select metabolite from loadings plot
#Last updated: 04/08/2025 (Jessica O'Loughlin)
def update_average_plots_plsda_UserGroupOrder(clickData, df_raw_T, df_norm, value_label):
    if clickData is None:
        raise PreventUpdate
    else:
        metabolite_name = str(clickData['points'][0]['customdata'][0]) 
        
        ### Average calculations on the transposed, raw data ###
        df_raw_T = pd.DataFrame(df_raw_T)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations 
        #Create list of columns names with str_variables + metabolite of interest
        columns_keep = set(df_raw_T.select_dtypes("object" or "str").columns)
        columns_keep.add(metabolite_name)
    
        #Create new df subset with data in columns_keep
        df_raw_T = df_raw_T[list(columns_keep)]
    
        #Calculate the average and standard deviations by Label group 
        df_average = pd.DataFrame(df_raw_T.groupby("Label")[metabolite_name].mean()).reset_index()
        df_average = df_average.rename(columns = {metabolite_name:"Mean"})
        
        df_stdev = pd.DataFrame(df_raw_T.groupby("Label")[metabolite_name].std()).reset_index()
        df_stdev = df_stdev.rename(columns = {metabolite_name:"STDEV"})
        
        #Merge the average and stdev results 
        df_graph = pd.concat([df_average, df_stdev["STDEV"]], axis = 1)
    
        fig_raw_plsda = go.Figure()
        fig_raw_plsda.add_trace(go.Bar(
            x=list(df_graph["Label"]),
            y=list(df_graph["Mean"]),
            error_y=dict(type='data', array=list(df_graph["STDEV"]))
        ))
        fig_raw_plsda.update_layout(title_text=metabolite_name, title_x=0.5, 
                         xaxis_title="Sample group", 
                         yaxis_title="Average Peak Intensity") 
        fig_raw_plsda.update_xaxes(categoryorder='array', categoryarray = value_label)
        
        ### Average calculations on the normalised data ###
        df_norm = pd.DataFrame(df_norm)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        #Create list of columns names with str_variables + metabolite of interest
        columns_keep_norm = set(df_norm.select_dtypes("object" or "str").columns)
        columns_keep_norm.add(metabolite_name)
    
        #Create new df subset with data in columns_keep
        df_norm = df_norm[list(columns_keep_norm)]
    
        #Calculate the average and standard deviations by Label group 
        df_average_norm = pd.DataFrame(df_norm.groupby("Label")[metabolite_name].mean()).reset_index()
        df_average_norm = df_average_norm.rename(columns = {metabolite_name:"Mean"})
        
        df_stdev_norm = pd.DataFrame(df_norm.groupby("Label")[metabolite_name].std()).reset_index()
        df_stdev_norm = df_stdev_norm.rename(columns = {metabolite_name:"STDEV"})
        
        #Merge the average and stdev results 
        df_graph_norm = pd.concat([df_average_norm, df_stdev_norm["STDEV"]], axis = 1)
    
        fig_norm_plsda = go.Figure()
        fig_norm_plsda.add_trace(go.Bar(
            x=list(df_graph_norm["Label"]),
            y=list(df_graph_norm["Mean"]),
            error_y=dict(type='data', array=list(df_graph_norm["STDEV"]))
        ))
        fig_norm_plsda.update_layout(title_text=metabolite_name, title_x=0.5, 
                         xaxis_title="Sample group", 
                         yaxis_title="Average Peak Intensity")
        fig_norm_plsda.update_xaxes(categoryorder='array', categoryarray = value_label)
        
        #Delete intermediate object (save memory space)
        del [metabolite_name, df_raw_T, columns_keep, df_average, df_stdev, 
             df_graph, df_norm, columns_keep_norm, df_average_norm, 
             df_stdev_norm, df_graph_norm]

    return fig_raw_plsda, fig_norm_plsda

#Update metabolite selection plots (PLSDA Tab)
#Last updated: 29/10/2025 (Jessica O'Loughlin)
def plsda_any_metab_plots_UserGroupOrder(n_clicks, data_raw, data_norm, rawplot_type, rawplot_axis, normplot_type, metabolite_name, value_label):
    if n_clicks is None:
        raise PreventUpdate
    else:
        metabolite_name = list(metabolite_name)
        
        data_raw = pd.DataFrame(data_raw)
        data_norm = pd.DataFrame(data_norm)

        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        #Create list of columns names with str_variables + metabolite of interest
        columns_keep = set(data_raw.select_dtypes("object" or "str").columns)
        columns_keep = columns_keep.union(metabolite_name)
        
        ##Calculations for average intensity bar plots + error bars (Normalised data)
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
        
        #label_order = list(df_average["Label"].unique())
        
        df_stdev_norm = pd.DataFrame(df_average_pre_norm.groupby(["Label", "Metabolites"]).std()).reset_index()
        df_stdev_norm = df_stdev_norm.rename(columns = {"Intensities":"STDEV"})
        
        ##Calculations for average intensity bar plots + error bars (Raw data)
        #Create new df subset with data in columns_keep
        df_average_pre = data_raw[list(columns_keep)]
        #Convert to long data format
        df_average_pre = pd.melt(df_average_pre, 
                                 id_vars = 'Label',
                                 var_name='Metabolites',
                                 value_name='Intensities',
                                 value_vars=list(metabolite_name))
        
        #Calculate the average and standard deviations by Label group 
        df_average = pd.DataFrame(df_average_pre.groupby(["Label", "Metabolites"]).mean()).reset_index()
        df_average = df_average.rename(columns = {"Intensities":"Mean"})
        
        df_stdev = pd.DataFrame(df_average_pre.groupby(["Label", "Metabolites"]).std()).reset_index()
        df_stdev = df_stdev.rename(columns = {"Intensities":"STDEV"})
        
        #Merge the average and stdev results 
        df_graph = pd.concat([df_average, df_stdev["STDEV"]], axis = 1)
        
        #If user selects Bar Plot for Raw data
        if rawplot_type == "Bar Plot":
            
            #If user selects Linear Y-axis
            if rawplot_axis == "Linear":
                plsda_any_metab_raw_fig = go.Figure()
                for metabolite in list(metabolite_name):
                    plsda_any_metab_raw_fig.add_trace(go.Bar(name=metabolite,
                                         x=df_graph['Label'].unique(),
                                         y=df_graph['Mean'][df_graph['Metabolites'] == metabolite],
                                         error_y=dict(type='data',
                                                      array=df_graph['STDEV'][df_graph['Metabolites'] == metabolite])))
                
                plsda_any_metab_raw_fig.update_layout(barmode='group', 
                                                      yaxis_title="Raw Intensities")
                plsda_any_metab_raw_fig.update_xaxes(categoryorder='array', 
                                                   categoryarray=value_label)
                
            #If user selects Log10 Y-axis
            else:
                plsda_any_metab_raw_fig = go.Figure()
                for metabolite in list(metabolite_name):
                    plsda_any_metab_raw_fig.add_trace(go.Bar(name=metabolite,
                                         x=df_graph['Label'].unique(),
                                         y=df_graph['Mean'][df_graph['Metabolites'] == metabolite],
                                         error_y=dict(type='data',
                                                      array=df_graph['STDEV'][df_graph['Metabolites'] == metabolite])))
                
                plsda_any_metab_raw_fig.update_layout(barmode='group', 
                                                      yaxis_title="Raw Intensities (log10)")
                plsda_any_metab_raw_fig.update_yaxes(type="log")
                plsda_any_metab_raw_fig.update_xaxes(categoryorder='array', 
                                                   categoryarray=value_label)
        
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
                plsda_any_metab_raw_fig = px.box(df_box, 
                                x = 'Label', 
                                y = 'Intensities', 
                                color = 'Metabolites', 
                                category_orders = {'Metabolites':list(metabolite_name), 
                                                   'Label':value_label}, 
                                labels={"Intensities": "Raw Intensities"},
                                )
            else:
                plsda_any_metab_raw_fig = px.box(df_box, 
                                x = 'Label', 
                                y = 'Intensities', 
                                color = 'Metabolites', 
                                category_orders = {'Metabolites':list(metabolite_name), 
                                                   'Label':value_label},
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
            
            #If user selects Linear Y-axis
            if rawplot_axis == 'Linear':
                plsda_any_metab_raw_fig = px.violin(df_violin, 
                                x = 'Label', 
                                y = 'Intensities', 
                                color = 'Metabolites', 
                                category_orders = {'Metabolites':list(metabolite_name), 
                                                    'Label':value_label}, 
                                labels={"Intensities": "Raw Intensities"},
                                )
            else:
                plsda_any_metab_raw_fig = px.violin(df_violin, 
                                x = 'Label', 
                                y = 'Intensities', 
                                color = 'Metabolites', 
                                category_orders = {'Metabolites':list(metabolite_name), 
                                                   'Label':value_label},
                                labels={"Intensities": "Raw Intensities (log10)"},
                                log_y = True
                                ) 
        
        #If user selects Bar Plot for Normalised data
        if normplot_type == "Bar Plot":
                    
            #Merge the average and stdev results 
            df_graph_norm = pd.concat([df_average_norm, df_stdev_norm["STDEV"]], axis = 1)
            
            plsda_any_metab_norm_fig = go.Figure()
            for metabolite in list(metabolite_name):
                plsda_any_metab_norm_fig.add_trace(go.Bar(name=metabolite,
                                     x=df_graph_norm['Label'].unique(),
                                     y=df_graph_norm['Mean'][df_graph_norm['Metabolites'] == metabolite],
                                     error_y=dict(type='data',
                                                  array=df_graph_norm['STDEV'][df_graph_norm['Metabolites'] == metabolite])))
            
            plsda_any_metab_norm_fig.update_layout(barmode='group', 
                                                   yaxis_title="Normalised Intensities")
            plsda_any_metab_norm_fig.update_xaxes(categoryorder='array', 
                                                  categoryarray=value_label)
                
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
            plsda_any_metab_norm_fig = px.box(df_box_norm, 
                            x = 'Label', 
                            y = 'Intensities', 
                            color = 'Metabolites', 
                            category_orders = {'Metabolites':list(metabolite_name),
                                               'Label':value_label}, 
                            labels={"Intensities": "Normalised Intensities"}
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
            plsda_any_metab_norm_fig = px.violin(df_violin_norm, 
                            x = 'Label', 
                            y = 'Intensities', 
                            color = 'Metabolites', 
                            category_orders = {'Metabolites':list(metabolite_name),
                                               'Label':value_label}, 
                            labels={"Intensities": "Normalised Intensities"}
                            )
            
        del [n_clicks, metabolite_name, data_raw, data_norm, 
             columns_keep, rawplot_type, df_average, df_stdev,
             df_graph, rawplot_axis, normplot_type]
        
    return plsda_any_metab_raw_fig, plsda_any_metab_norm_fig

#Make Volcano plot
#Last updated: 10/11/2025 (Jessica O'Loughlin)
def volcanic_eruption_FCThreshold(n_clicks, data, state_1, state_2, sig_thres, fc_thres, labelYes):
    if n_clicks is None:
        raise PreventUpdate
    else: #Only update the volcano plot if button is clicked
        df_raw_transposed = pd.DataFrame(data)
        #Remove the Label column
        #df_raw_transposed = df_raw_transposed.drop(['Label'], axis = 1)
        #Save user-selected groups as lists
        sel_1 = list(state_1)
        sel_2 = list(state_2)
        
        #Make list with all the samples selected
        total_sel = sel_1 + sel_2
        #Subset the raw data to only have these samples
        df_raw_transposed = df_raw_transposed[df_raw_transposed['Label'].isin(total_sel)]
        #Reset index
        df_raw_transposed = df_raw_transposed.reset_index(drop = True)
        
        ##Normalise this data
        #Log transform numeric columns
        df_sel = df_raw_transposed.apply(lambda x: np.log10(x) if np.issubdtype(x.dtype, np.number) else x)
        #Mean-centre scaling
        df_sel = df_sel.apply(lambda x: x-x.mean() if np.issubdtype(x.dtype, np.number) else x)
        #Pareto scaling
        df_sel = df_sel.apply(lambda x: x/math.sqrt(x.std()) if np.issubdtype(x.dtype, np.number) else x)
        #Remove metabolites where NaNs are introduced 
        #E.g. when Sample subsetting makes STDEV = 0 --> get divide by 0 error
        df_sel = df_sel.dropna(axis=1)
        
        #Only keep the metabolites in the normalised data in the raw data
        keep_columns = list(df_sel.columns)
        df_raw_transposed = df_raw_transposed[keep_columns]
        
        ##Split the data into the two user-defined groups
        #Raw data
        df_1_raw = df_raw_transposed[df_raw_transposed['Label'].isin(sel_1)]
        df_2_raw = df_raw_transposed[df_raw_transposed['Label'].isin(sel_2)]
        #Normalised data
        df_1_norm = df_sel[df_sel['Label'].isin(sel_1)]
        df_2_norm = df_sel[df_sel['Label'].isin(sel_2)]
        #Reset index
        df_1_raw = df_1_raw.reset_index(drop = True)
        df_2_raw = df_2_raw.reset_index(drop = True)
        df_1_norm = df_1_norm.reset_index(drop = True)
        df_2_norm = df_2_norm.reset_index(drop = True)
        #Remove Sample and Label columns
        df_1_raw = df_1_raw.drop(['Sample', 'Label'], axis = 1)
        df_2_raw = df_2_raw.drop(['Sample', 'Label'], axis = 1)
        df_1_norm = df_1_norm.drop(['Sample', 'Label'], axis = 1)
        df_2_norm = df_2_norm.drop(['Sample', 'Label'], axis = 1)
        
        ##Fold Change (FC) calculations
        #Calculate the average intensity for each metabolite in each group
        df_1_raw_mean = df_1_raw.mean(axis = 0)
        df_2_raw_mean = df_2_raw.mean(axis = 0)
        #Calculate Log2(FC)
        df_fc = pd.DataFrame(np.log2(df_2_raw_mean / df_1_raw_mean))
        #Reset index
        df_fc = df_fc.reset_index()
        #Rename columns
        df_fc = df_fc.rename(columns = {"index":"Metabolite", 0:"Fold-Change(log2)"})
        #Reset index
        df_fc = df_fc.reset_index(drop=True)
        #Add column indicating which group the metabolites are elevated in
        df_fc.loc[df_fc["Fold-Change(log2)"] < 0, "Group"] = "Group 1"
        df_fc.loc[df_fc["Fold-Change(log2)"] > 0, "Group"] = "Group 2"
        
        ##Calculate p-values betweeen the groups for each metabolite
        #Create dataframe for p-values to go into
        p_val_df = pd.DataFrame({"Metabolite":[], "p-value":[]})
        for column in df_1_norm:
            #Calculate the p-value
            p_val = stats.ttest_ind(df_1_norm[column],
                            df_2_norm[column])
            #Add to dataframe 
            add_value = pd.DataFrame({"Metabolite":[column], 
                                      "p-value":[p_val[1]]})
            p_val_df = pd.concat([p_val_df, add_value])
        #Reset index
        p_val_df = p_val_df.reset_index(drop = True)
        #Transform p-values (log10)
        p_val_df['p-value(-log10)'] = np.log10(p_val_df['p-value'])
        #Multiply by -1 (-log10)
        p_val_df['p-value(-log10)'] = p_val_df['p-value(-log10)'].apply(lambda x: x*-1)
        
        #Join the FC and p-value dataframes together by Metabolite
        df_fc_p_val = pd.merge(df_fc, p_val_df, on='Metabolite', how='inner')
        #Default colour
        df_fc_p_val['colour'] = 'blue'
        
        #Put p-value threshold into -log10 scale
        if sig_thres != None:
            sig_thres = (math.log(sig_thres, 10))*-1
        
        #Make FC value absolute for the calculations (in case someone puts in a -ve number)
        if fc_thres != None:
            fc_thres = abs(fc_thres)
            #Put FC threshold into log2 scale
            fc_thres = math.log(fc_thres, 2)

        #Add threshold lines
        if sig_thres is None and fc_thres is None:
            #If no thresolds or labels are defined: return the 'plain' plot
            volcano_plot = px.scatter(df_fc_p_val, 
                                      x="Fold-Change(log2)",
                                      y="p-value(-log10)", 
                                      color = 'colour', 
                                      color_discrete_map={'blue': 'blue'},
                                      hover_data = ["Metabolite", "Group", 
                                                    "p-value"], 
                                      custom_data=["Metabolite"], 
                                      height=800)
            volcano_plot.update_layout(showlegend=False)
            volcano_plot.update_xaxes(tickfont=dict(size=20), 
                                      title_font = {"size": 24})
            volcano_plot.update_yaxes(tickfont=dict(size=20), 
                                      title_font = {"size": 24})
            
        else: 
            if sig_thres != None and fc_thres != None: #Add p-value and FC lines
                #Make selected data points red
                #Keep data within p-value and FC thresolds
                df_fc_p_val_sub = df_fc_p_val[df_fc_p_val['p-value(-log10)'] >= sig_thres]
                df_fc_p_val_sub = df_fc_p_val_sub[(df_fc_p_val_sub['Fold-Change(log2)'] > fc_thres) | (df_fc_p_val_sub['Fold-Change(log2)'] < fc_thres*-1)]  
                #Make specific metabolites correspond to red
                for idx in list(df_fc_p_val_sub.index):
                    df_fc_p_val.at[idx, 'colour'] = 'red'
                volcano_plot = px.scatter(df_fc_p_val, 
                                          x="Fold-Change(log2)",
                                          y="p-value(-log10)", 
                                          color = 'colour', 
                                          color_discrete_map={'red': 'red', 'blue': 'blue'},
                                          hover_data = ["Metabolite", "Group", "p-value"], 
                                          custom_data=["Metabolite"], 
                                          height=800)
                volcano_plot.update_layout(showlegend=False)
                
                #Add required lines
                volcano_plot.add_hline(y=sig_thres, 
                                       line_dash="dash", 
                                       line_color="green")
                volcano_plot.add_vline(x=fc_thres, 
                                       line_dash="dash",
                                       line_color="purple")
                #multiply fc_thres by -1 --> get line on both sides of the volcano plot
                volcano_plot.add_vline(x=fc_thres*-1, 
                                       line_dash="dash",
                                       line_color="purple")
                volcano_plot.update_xaxes(tickfont=dict(size=20), 
                                          title_font = {"size": 24})
                volcano_plot.update_yaxes(tickfont=dict(size=20), 
                                          title_font = {"size": 24})

            elif sig_thres != None: #add p-value line
                #Make selected data points red
                #Keep data within p-value and FC thresolds
                df_fc_p_val_sub = df_fc_p_val[df_fc_p_val['p-value(-log10)'] >= sig_thres]
                #Make specific metabolites correspond to red
                for idx in list(df_fc_p_val_sub.index):
                    df_fc_p_val.at[idx, 'colour'] = 'red'
                volcano_plot = px.scatter(df_fc_p_val, 
                                          x="Fold-Change(log2)",
                                          y="p-value(-log10)", 
                                          color = 'colour', 
                                          color_discrete_map={'red': 'red', 'blue': 'blue'},
                                          hover_data = ["Metabolite", "Group", "p-value"], 
                                          custom_data=["Metabolite"], 
                                          height=800)
                volcano_plot.update_layout(showlegend=False)
                #Add p-value line
                volcano_plot.add_hline(y=sig_thres, 
                                       line_dash="dash", 
                                       line_color="green")
                volcano_plot.update_xaxes(tickfont=dict(size=20), 
                                          title_font = {"size": 24})
                volcano_plot.update_yaxes(tickfont=dict(size=20), 
                                          title_font = {"size": 24})
            elif fc_thres != None: #Add Fold-Change lines
                #Make selected data points red
                #Keep data within p-value and FC thresolds
                df_fc_p_val_sub = df_fc_p_val[(df_fc_p_val['Fold-Change(log2)'] > fc_thres) | (df_fc_p_val['Fold-Change(log2)'] < fc_thres*-1)]  
                #Make specific metabolites correspond to red
                for idx in list(df_fc_p_val_sub.index):
                    df_fc_p_val.at[idx, 'colour'] = 'red'
                volcano_plot = px.scatter(df_fc_p_val, 
                                          x="Fold-Change(log2)",
                                          y="p-value(-log10)", 
                                          color = 'colour', 
                                          color_discrete_map={'red': 'red', 'blue': 'blue'},
                                          hover_data = ["Metabolite", "Group", "p-value"], 
                                          custom_data=["Metabolite"], 
                                          height=800)
                volcano_plot.update_layout(showlegend=False)
                #Add Fold-Change lines
                volcano_plot.add_vline(x=fc_thres, 
                                       line_dash="dash",
                                       line_color="purple")
                #multiply fc_thres by -1 --> get line on both sides of the volcano plot
                volcano_plot.add_vline(x=fc_thres*-1, 
                                       line_dash="dash",
                                       line_color="purple")
                volcano_plot.update_xaxes(tickfont=dict(size=20), 
                                          title_font = {"size": 24})
                volcano_plot.update_yaxes(tickfont=dict(size=20), 
                                          title_font = {"size": 24})
        
        #Add labels to significant metabolites        
        if labelYes is None or labelYes == []: #If not selected by user
            pass
        else:
            if sig_thres != None and fc_thres != None: #p-value & FC selected by user
                #Keep data within p-value and FC thresolds
                df_fc_p_val_sub = df_fc_p_val[df_fc_p_val['p-value(-log10)'] >= sig_thres]
                df_fc_p_val_sub = df_fc_p_val_sub[(df_fc_p_val_sub['Fold-Change(log2)'] > fc_thres) | (df_fc_p_val_sub['Fold-Change(log2)'] < fc_thres*-1)]      
                # Add annotations for specific points
                for idx in list(df_fc_p_val_sub.index):
                    volcano_plot.add_annotation(x=df_fc_p_val_sub.loc[idx, 'Fold-Change(log2)'], 
                                                y=df_fc_p_val_sub.loc[idx, 'p-value(-log10)'],
                                       text=df_fc_p_val_sub.loc[idx, 'Metabolite']
                                       )
            elif sig_thres != None: #p-value only selected by user
                df_fc_p_val_sub = df_fc_p_val[df_fc_p_val['p-value(-log10)'] >= sig_thres]
                # Add annotations for specific points
                for idx in list(df_fc_p_val_sub.index):
                    volcano_plot.add_annotation(x=df_fc_p_val_sub.loc[idx, 'Fold-Change(log2)'], 
                                                y=df_fc_p_val_sub.loc[idx, 'p-value(-log10)'],
                                       text=df_fc_p_val_sub.loc[idx, 'Metabolite']
                                       )
            elif fc_thres != None: #FC only selected by user
                df_fc_p_val_sub = df_fc_p_val[(df_fc_p_val['Fold-Change(log2)'] > fc_thres) | (df_fc_p_val['Fold-Change(log2)'] < fc_thres*-1)]      
                # Add annotations for specific points
                for idx in list(df_fc_p_val_sub.index):
                    volcano_plot.add_annotation(x=df_fc_p_val_sub.loc[idx, 'Fold-Change(log2)'], 
                                                y=df_fc_p_val_sub.loc[idx, 'p-value(-log10)'],
                                       text=df_fc_p_val_sub.loc[idx, 'Metabolite']
                                       )
            else:
                #Just add labels to everything
                for idx in list(df_fc_p_val.index):
                    volcano_plot.add_annotation(x=df_fc_p_val.loc[idx, 'Fold-Change(log2)'], 
                                                y=df_fc_p_val.loc[idx, 'p-value(-log10)'],
                                                text=df_fc_p_val.loc[idx, 'Metabolite']
                                                )
                
        
        #Delete intermediate object (save memory space)
        del [df_raw_transposed, sel_1, sel_2, total_sel, df_sel, keep_columns, 
             df_1_raw, df_1_norm, df_1_raw_mean, df_2_raw, df_2_norm, df_2_raw_mean, 
             df_fc, p_val_df, df_fc_p_val]
    
    return volcano_plot

#Create custom heatmaps
#Last updated: 04/08/2025 (Jessica O'Loughlin)
def CustomHeatmap(n_clicks, data, SelectedGroups, SelectedMetabolites):
    if n_clicks is None:
        raise PreventUpdate
    else:
    
        dff = pd.DataFrame(data)
        
        dff = dff.set_index('Sample')
        #Remove Sample info + set Label column as the index
        dff = dff.set_index('Label')
        
        ##Generate heat map with selected sample groups and metabolites
        #Scale each column (metabolite) individually
        scaler = MinMaxScaler()
        scaled_df = pd.DataFrame(scaler.fit_transform(dff), columns=dff.columns)
        scaled_df.index = list(dff.index)
        
        ### Heatmap for Label averages ###
        #Calculate the average scaled peak intensities by Label (group)
        #Where the label is the index
        label_groups = scaled_df.groupby(scaled_df.index)
        mean_scaled_df = label_groups.mean()
        #Only keep user selected metabolites
        mean_scaled_df = mean_scaled_df[list(SelectedMetabolites)]
        #Transpose the dataframe (show metabolites as rows)
        mean_scaled_df = mean_scaled_df.transpose()
        #Only Keep user selected sample groups
        mean_scaled_df = mean_scaled_df[list(SelectedGroups)]
        
        #Plot group-average heat map
        if len(SelectedMetabolites) < 10:
            custom_heatmap = px.imshow(mean_scaled_df,
                                       aspect = 'equal', 
                                       color_continuous_scale='Blues', 
                                       # height = 80*len(mean_scaled_df), 
                                       # width = 30*len(mean_scaled_df.columns)
                                       )
            
            return custom_heatmap
        
        else:
            custom_heatmap = px.imshow(mean_scaled_df,
                                       aspect = 'equal', 
                                       color_continuous_scale='Blues', 
                                       height = 40*len(mean_scaled_df), 
                                       # width = 1000*len(mean_scaled_df.columns)
                                       )
    
            return custom_heatmap
        
        del [dff, scaler, scaled_df, label_groups, mean_scaled_df, 
             n_clicks, data, SelectedGroups, SelectedMetabolites]

#Download volcano plot data
#Last updated: 04/08/2025 (Jessica O'Loughlin)        
def volcanic_eruption_download(n_clicks, data_raw, state_1, state_2, sig_thres, data_norm, project_no):
    if n_clicks is None:
        raise PreventUpdate
    else: #Only update the volcano plot if button is clicked
        df_raw_transposed = pd.DataFrame(data_raw)
        #Save user-selected groups as lists
        sel_1 = list(state_1)
        sel_2 = list(state_2)
        
        #Make list with all the samples selected
        total_sel = sel_1 + sel_2
        #Subset the raw data to only have these samples
        df_raw_transposed = df_raw_transposed[df_raw_transposed['Label'].isin(total_sel)]
        #Reset index
        df_raw_transposed = df_raw_transposed.reset_index(drop = True)
        
        ##Normalise this data
        #Log transform numeric columns
        df_sel = df_raw_transposed.apply(lambda x: np.log10(x) if np.issubdtype(x.dtype, np.number) else x)
        #Mean-centre scaling
        df_sel = df_sel.apply(lambda x: x-x.mean() if np.issubdtype(x.dtype, np.number) else x)
        #Pareto scaling
        df_sel = df_sel.apply(lambda x: x/math.sqrt(x.std()) if np.issubdtype(x.dtype, np.number) else x)
        #Remove metabolites where NaNs are introduced 
        #E.g. when Sample subsetting makes STDEV = 0 --> get divide by 0 error
        df_sel = df_sel.dropna(axis=1)
        
        #Only keep the metabolites in the normalised data in the raw data
        keep_columns = list(df_sel.columns)
        df_raw_transposed = df_raw_transposed[keep_columns]
        
        ##Split the data into the two user-defined groups
        #Raw data
        df_1_raw = df_raw_transposed[df_raw_transposed['Label'].isin(sel_1)]
        df_2_raw = df_raw_transposed[df_raw_transposed['Label'].isin(sel_2)]
        #Normalised data
        df_1_norm = df_sel[df_sel['Label'].isin(sel_1)]
        df_2_norm = df_sel[df_sel['Label'].isin(sel_2)]
        #Reset index
        df_1_raw = df_1_raw.reset_index(drop = True)
        df_2_raw = df_2_raw.reset_index(drop = True)
        df_1_norm = df_1_norm.reset_index(drop = True)
        df_2_norm = df_2_norm.reset_index(drop = True)
        #Remove Sample and Label columns
        df_1_raw = df_1_raw.drop(['Sample', 'Label'], axis = 1)
        df_2_raw = df_2_raw.drop(['Sample', 'Label'], axis = 1)
        df_1_norm = df_1_norm.drop(['Sample', 'Label'], axis = 1)
        df_2_norm = df_2_norm.drop(['Sample', 'Label'], axis = 1)
        
        ##Fold Change (FC) calculations
        #Calculate the average intensity for each metabolite in each group
        df_1_raw_mean = df_1_raw.mean(axis = 0)
        df_2_raw_mean = df_2_raw.mean(axis = 0)
        #Calculate Log2(FC)
        #df_fc = pd.DataFrame(np.log2(df_1_raw_mean / df_2_raw_mean))
        df_fc = pd.DataFrame(np.log2(df_2_raw_mean / df_1_raw_mean))
        #Reset index
        df_fc = df_fc.reset_index()
        #Rename columns
        df_fc = df_fc.rename(columns = {"index":"Metabolite", 0:"Fold-Change(log2)"})
        #Reset index
        df_fc = df_fc.reset_index(drop=True)
        #Add column indicating which group the metabolites are elevated in
        df_fc.loc[df_fc["Fold-Change(log2)"] < 0, "Group"] = "Group 1"
        df_fc.loc[df_fc["Fold-Change(log2)"] > 0, "Group"] = "Group 2"
        
        ##Calculate p-values betweeen the groups for each metabolite
        #Create dataframe for p-values to go into
        p_val_df = pd.DataFrame({"Metabolite":[], "p-value":[]})
        for column in df_1_norm:
            #Calculate the p-value
            p_val = stats.ttest_ind(df_1_norm[column],
                            df_2_norm[column])
            #Add to dataframe 
            add_value = pd.DataFrame({"Metabolite":[column], 
                                      "p-value":[p_val[1]]})
            p_val_df = pd.concat([p_val_df, add_value])
        #Reset index
        p_val_df = p_val_df.reset_index(drop = True)
        #Transform p-values (log10)
        p_val_df['p-value(-log10)'] = np.log10(p_val_df['p-value'])
        #Multiply by -1 (-log10)
        p_val_df['p-value(-log10)'] = p_val_df['p-value(-log10)'].apply(lambda x: x*-1)
        
        #Join the FC and p-value dataframes together by Metabolite
        df_fc_p_val = pd.merge(df_fc, p_val_df, on='Metabolite', how='inner')
        
        #Sort values by Group and Significance value (easier to read output)
        df_fc_p_val = df_fc_p_val.sort_values(['Group', 'p-value(-log10)'], 
                                              ascending = [True, False])
        #Reorder columns (more sensible order to the reader)
        df_fc_p_val = df_fc_p_val.loc[:,['Metabolite','Group','p-value', 
                                         'p-value(-log10)', 'Fold-Change(log2)']]
        
        #Merge raw and normalised data to dataframe
        metabolites_keep = list(df_fc_p_val['Metabolite'])
        str_variables = set(pd.DataFrame(data_norm).select_dtypes("object" or "str").columns)
        columns_keep = list(str_variables) + metabolites_keep
        
        keep_raw = df_raw_transposed[df_raw_transposed.columns[df_raw_transposed.columns.isin(columns_keep)]]
        data_norm = pd.DataFrame(data_norm)
        #Subset the raw data to only have these samples
        data_norm = data_norm[data_norm['Label'].isin(total_sel)]
        #Reset index
        data_norm = data_norm.reset_index(drop = True)
        keep_norm = data_norm[data_norm.columns[data_norm.columns.isin(columns_keep)]]
        
        keep_raw = keep_raw.transpose()
        keep_norm = keep_norm.transpose()
        
        #Set first row as column names, remove that row from main dataframe + reset index
        keep_raw.columns = keep_raw.loc['Sample']
        keep_raw = keep_raw.drop(['Sample', 'Label'])
        keep_raw = keep_raw.add_suffix('_raw')
        keep_raw = keep_raw.reset_index(names = 'Metabolite')
        
        keep_norm.columns = keep_norm.loc['Sample']
        keep_norm = keep_norm.drop(['Sample', 'Label'])
        keep_norm = keep_norm.add_suffix('_norm')
        keep_norm = keep_norm.reset_index(names = 'Metabolite')
        
        #Merge raw and normalised intensities for metabolites in volcano data
        df_fc_p_val = pd.merge(df_fc_p_val, keep_raw, on='Metabolite', how='inner')
        df_fc_p_val = pd.merge(df_fc_p_val, keep_norm, on='Metabolite', how='inner')
        
        #Create information sheet content
        volcano_info_sheet = pd.DataFrame({'Column': ['Metabolite', 
                                     'Group', 
                                     'p-value', 
                                     'p-value(-log10)', 
                                     'Fold-Change(log2)', 
                                     '[sample_name]_raw', 
                                     '[sample_name]_norm'],
                          'Explanation': ['Metabolites present in the samples used to generate the volcano plot', 
                                          'Denotes which group the metabolite was elevated in from the user-selected groups on the volcano plot page', 
                                          'P-value (calculated from the normalised data) of that metabolite its group', 
                                          'The p-value transformed by -log to the base 10', 
                                          'The Fold Change (calculated from the raw data) of the metabolite in that group transformed to log to the base 2', 
                                          'The raw intensity of each respective metabolite for that sample in groups selected for the volcano plot calculations', 
                                          'The normalised intensity of each respective metabolite for that sample in groups selected for the volcano plot calculations']})

        writer = pd.ExcelWriter(f"EdinOmics_{project_no}_Volcano_plot_data.xlsx", 
                        engine = 'xlsxwriter')

        volcano_info_sheet.to_excel(writer, sheet_name = 'ReadMe', index = False)
        df_fc_p_val.to_excel(writer, sheet_name = 'VolcanoData', index = False)
        
        writer.close()
        
        #Delete intermediate object (save memory space)
        del [df_raw_transposed, sel_1, sel_2, total_sel, df_sel, keep_columns, 
             df_1_raw, df_1_norm, df_1_raw_mean, df_2_raw, df_2_norm, df_2_raw_mean, 
             df_fc, p_val_df, df_fc_p_val, metabolites_keep, str_variables, 
             columns_keep, keep_raw, keep_norm, volcano_info_sheet, writer]

#Select metabolite from volcano plot
#Last updated: 29/10/2025 (Jessica O'Loughlin)
def update_average_plots_volcano_SeleData(clickData, df_raw_T, df_norm, state_1, state_2):
    if clickData is None:
        raise PreventUpdate
    else:
        metabolite_name = str(clickData['points'][0]['customdata'][0]) 
        
        ### Average calculations on the transposed, raw data ###
        df_raw_T = pd.DataFrame(df_raw_T)
        
        #Added 20/10/2025: subset the data so that only the volcano plot groups are included
        #Save user-selected groups as lists
        sel_1 = list(state_1)
        sel_2 = list(state_2)
        #Make list with all the samples selected
        total_sel = sel_1 + sel_2
        #Subset the raw data to only have these samples
        df_raw_T = df_raw_T[df_raw_T['Label'].isin(total_sel)]
        #Reset index
        df_raw_T = df_raw_T.reset_index(drop = True)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        #Create list of columns names with str_variables + metabolite of interest
        columns_keep = set(df_raw_T.select_dtypes("object" or "str").columns)
        columns_keep.add(metabolite_name)
    
        #Create new df subset with data in columns_keep
        df_raw_T = df_raw_T[list(columns_keep)]
    
        #Calculate the average and standard deviations by Label group 
        df_average = pd.DataFrame(df_raw_T.groupby("Label")[metabolite_name].mean()).reset_index()
        df_average = df_average.rename(columns = {metabolite_name:"Mean"})
        
        df_stdev = pd.DataFrame(df_raw_T.groupby("Label")[metabolite_name].std()).reset_index()
        df_stdev = df_stdev.rename(columns = {metabolite_name:"STDEV"})
        
        #Merge the average and stdev results 
        df_graph = pd.concat([df_average, df_stdev["STDEV"]], axis = 1)
    
        fig_raw_volcano = go.Figure()
        fig_raw_volcano.add_trace(go.Bar(
            x=list(df_graph["Label"]),
            y=list(df_graph["Mean"]),
            error_y=dict(type='data', array=list(df_graph["STDEV"]))
        ))
        fig_raw_volcano.update_layout(title_text=metabolite_name, title_x=0.5, 
                         xaxis_title="Sample group", 
                         yaxis_title="Average Peak Intensity") 
        fig_raw_volcano.update_xaxes(categoryorder='array', categoryarray = total_sel)
        
        ### Average calculations on the normalised data ###
        df_norm = pd.DataFrame(df_norm)
        
        #Added 20/10/2025: subset the data so that only the volcano plot groups are included
        #Subset the raw data to only have these samples
        df_norm = df_norm[df_norm['Label'].isin(total_sel)]
        #Reset index
        df_norm = df_norm.reset_index(drop = True)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        #Create list of columns names with str_variables + metabolite of interest
        columns_keep_norm = set(df_norm.select_dtypes("object" or "str").columns)
        columns_keep_norm.add(metabolite_name)
    
        #Create new df subset with data in columns_keep
        df_norm = df_norm[list(columns_keep_norm)]
    
        #Calculate the average and standard deviations by Label group 
        df_average_norm = pd.DataFrame(df_norm.groupby("Label")[metabolite_name].mean()).reset_index()
        df_average_norm = df_average_norm.rename(columns = {metabolite_name:"Mean"})
        
        df_stdev_norm = pd.DataFrame(df_norm.groupby("Label")[metabolite_name].std()).reset_index()
        df_stdev_norm = df_stdev_norm.rename(columns = {metabolite_name:"STDEV"})
        
        #Merge the average and stdev results 
        df_graph_norm = pd.concat([df_average_norm, df_stdev_norm["STDEV"]], axis = 1)
    
        fig_norm_volcano = go.Figure()
        fig_norm_volcano.add_trace(go.Bar(
            x=list(df_graph_norm["Label"]),
            y=list(df_graph_norm["Mean"]),
            error_y=dict(type='data', array=list(df_graph_norm["STDEV"]))
        ))
        fig_norm_volcano.update_layout(title_text=metabolite_name, title_x=0.5, 
                         xaxis_title="Sample group", 
                         yaxis_title="Average Peak Intensity")
        fig_norm_volcano.update_xaxes(categoryorder='array', categoryarray = total_sel)
        
        #Delete intermediate object (save memory space)
        del [metabolite_name, df_raw_T, columns_keep, df_average, df_stdev, 
             df_graph, df_norm, columns_keep_norm, df_average_norm, 
             df_stdev_norm, df_graph_norm]

    return fig_raw_volcano, fig_norm_volcano

#Download raw, transposed data
#Last updated: 04/08/2025 (Jessica O'Loughlin)
def raw_transposed_data_download(n_clicks, n_clicks_inTab, data, project_no):
    if n_clicks or n_clicks_inTab is None:
        raise PreventUpdate
    else:
        df_raw_save = pd.DataFrame(data)
        
        #Create information sheet content      
        raw_info_sheet = pd.DataFrame({'Column': ['Sample', 
                                     'Label', 
                                     'Metabolite names'],
                          'Explanation': ['Each individual sample name', 
                                          'The group each sample belongs to', 
                                          'The raw intensities for each metabolite in the samples you selected in the interactive report']})
        
        writer = pd.ExcelWriter(f"EdinOmics_{project_no}_raw_data.xlsx", 
                                engine = 'xlsxwriter')
        
        raw_info_sheet.to_excel(writer, sheet_name = 'ReadMe', index = False)
        df_raw_save.to_excel(writer, sheet_name = 'RawData', index = False)
        
        writer.close()
        
#Download Normalised data file with selected samples as .xlsx        
def processed_data_download(n_clicks, n_clicks_inTab, data, project_no):
    if n_clicks or n_clicks_inTab is None:
        raise PreventUpdate
    else:
        df_proc_save = pd.DataFrame(data)
        
        #Create information sheet content      
        norm_info_sheet = pd.DataFrame({'Column': ['Sample', 
                                     'Label', 
                                     'Metabolite names'],
                          'Explanation': ['Each individual sample name', 
                                          'The group each sample belongs to', 
                                          'The normalised intensities for each metabolite in the samples you selected in the interactive report']})
        
        writer = pd.ExcelWriter(f"EdinOmics_{project_no}_normalised_data.xlsx", 
                                engine = 'xlsxwriter')
        
        norm_info_sheet.to_excel(writer, sheet_name = 'ReadMe', index = False)
        df_proc_save.to_excel(writer, sheet_name = 'NormalisedData', index = False)
        
        writer.close()

#Download PCA scores file with selected samples as .xlsx 
#Last updated: 04/08/2025 (Jessica O'Loughlin)       
def pca_download_scores(n_clicks, n_clicks_inTab, data, project_no):
    
    if n_clicks or n_clicks_inTab is None:
        raise PreventUpdate
    else:
        pca_df_str = pd.DataFrame(data)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        str_variables = set(pca_df_str.select_dtypes("object" or "str").columns)
        
        #Only keep numerical variables (remove strings)
        pca_df = pca_df_str.drop(str_variables, axis = 1)
        pca_df = pca_df.apply(pd.to_numeric, errors='coerce', axis=1)
        
        pca_3D = PCA(n_components=3)
        components_3D_selected = pca_3D.fit_transform(pca_df)
        
        components_3D_selected = pd.DataFrame(components_3D_selected)
        
        #Get a list of column headers
        column_list = list(pca_df_str.columns)
        #Automatically generate list of metabolites
        
        #Remove the str_variables to get metabolites only
        metabolite_list = [metabolite for metabolite in 
                           column_list if metabolite not in list(str_variables)]
        #Remove metabolites (only keep sample labels)
        pca_df_str = pca_df_str.drop(metabolite_list, axis = 1)
        
        #Concatenate the PCA outputs and the sample/label IDs together
        components_3D_selected = pd.concat([pca_df_str.reset_index(drop = True), 
                                    components_3D_selected], 
                                   axis = 1)
    
        component_save = components_3D_selected.rename(columns={
            0: 'PC1', 
            1: 'PC2', 
            2: 'PC3',})
        
        #Create information sheet content      
        pcaScores_info_sheet = pd.DataFrame({'Column': ['Sample', 
                                     'Label', 
                                     'PC1',
                                     'PC2',
                                     'PC3'],
                          'Explanation': ['Each individual sample name', 
                                          'The group each sample belongs to', 
                                          'Position of the sample datapoint along the PC1 axis', 
                                          'Position of the sample datapoint along the PC2 axis', 
                                          'Position of the sample datapoint along the PC3 axis']})
        
        writer = pd.ExcelWriter(f"EdinOmics_{project_no}_pca_scores_results.xlsx", 
                                engine = 'xlsxwriter')
        # writer = pd.ExcelWriter("EdinOmics_pca_scores_results.xlsx", 
        #                         engine = 'xlsxwriter')
        
        pcaScores_info_sheet.to_excel(writer, sheet_name = 'ReadMe', index = False)
        component_save.to_excel(writer, sheet_name = 'PCAScores', index = False)
        
        writer.close()

#Download PCA loadings file with selected samples as .xlsx    
#Last updated: 04/08/2025 (Jessica O'Loughlin)    
def pca_download_loadings(n_clicks, n_clicks_inTab, data, project_no):
    if n_clicks or n_clicks_inTab is None:
        raise PreventUpdate
    else:
        pca_df_str = pd.DataFrame(data)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        str_variables = set(pca_df_str.select_dtypes("object" or "str").columns)
        
        #Only keep numerical variables (remove strings)
        pca_df = pca_df_str.drop(str_variables, axis = 1)
        pca_df = pca_df.apply(pd.to_numeric, errors='coerce', axis=1)
        
        pca_2D = PCA(n_components=3)
        components_2D_selected = pca_2D.fit_transform(pca_df)
        
        components_2D_selected = pd.DataFrame(components_2D_selected)
        
        #Get a list of column headers
        column_list = list(pca_df_str.columns)
        #Automatically generate list of metabolites
        
        #Remove the str_variables to get metabolites only
        metabolite_list = [metabolite for metabolite in 
                           column_list if metabolite not in list(str_variables)]
        
        #Save Loadings axis 1 as a data frame
        loadings = pd.DataFrame(pca_2D.components_[0])
        #Rename column
        loadings = loadings.rename(columns = {0:"Loadings 1"})
        #Save Loadings axis 2 as a list
        loadings_pc2 = list(pca_2D.components_[1])
        #Add Loadings axis 2 to the dataframe
        loadings["Loadings 2"] = loadings_pc2
        #Save Loadings axis 3 as a list
        loadings_pc3 = list(pca_2D.components_[2])
        #Add Loadings axis 3 to the dataframe
        loadings["Loadings 3"] = loadings_pc3
        #Add the metabolite list to the loadings data
        loadings["Metabolite"] = metabolite_list 
        #Reorder columns
        loadings = loadings.loc[:,["Metabolite", "Loadings 1", "Loadings 2", 
                                   "Loadings 3"]]
        
        #Create information sheet content      
        pcaLoadings_info_sheet = pd.DataFrame({'Column': ['Metabolite',  
                                     'Loadings 1',
                                     'Loadings 2',
                                     'Loadings 3'],
                          'Explanation': ['Metabolites present in the user-selected data from the interactive report', 
                                          'Position of the metabolite datapoint along the Loadings 1 axis', 
                                          'Position of the metabolite datapoint along the Loadings 2 axis', 
                                          'Position of the metabolite datapoint along the Loadings 3 axis']})
        
        writer = pd.ExcelWriter(f"EdinOmics_{project_no}_pca_loadings_results.xlsx", 
                                engine = 'xlsxwriter')
        
        pcaLoadings_info_sheet.to_excel(writer, sheet_name = 'ReadMe', index = False)
        loadings.to_excel(writer, sheet_name = 'PCALoadings', index = False)
        
        writer.close()

#Download PCA VIP scores file with selected samples as .xlsx  
#Last updated: 04/08/2025 (Jessica O'Loughlin)      
def pca_download_vip_scores(n_clicks, n_clicks_inTab, data, project_no):
    if n_clicks or n_clicks_inTab is None:
        raise PreventUpdate
    else:
        pca_df_str = pd.DataFrame(data)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        str_variables = set(pca_df_str.select_dtypes("object" or "str").columns)
        
        #Only keep numerical variables (remove strings)
        pca_df = pca_df_str.drop(str_variables, axis = 1)
        pca_df = pca_df.apply(pd.to_numeric, errors='coerce', axis=1)
        
        pca_2D = PCA(n_components=3)
        pca_2D.fit_transform(pca_df)
        
        # Change pcs components ndarray to a dataframe
        importance_df = pd.DataFrame(pca_2D.components_)
        # Assign columns
        importance_df.columns = pca_df.columns
        # Change to absolute values
        importance_df =importance_df.apply(np.abs)
        # Transpose
        importance_df=importance_df.transpose()
        # Change column names again
        ## First get number of pcs
        num_pcs = importance_df.shape[1]
        ## Generate the new column names
        new_columns = [f'PC{i} VIP score' for i in range(1, num_pcs + 1)]
        ## Now rename
        importance_df.columns = new_columns
        #Multiply VIP score values by 10
        importance_df = importance_df.apply(lambda x: x*10)
        
        #PCA axis 1 top 50 important features
        pca_top_50_features = importance_df['PC1 VIP score'].sort_values(ascending = False)[:50]
        pca_top_50_features = pca_top_50_features.reset_index()
        pca_top_50_features = pca_top_50_features.rename(columns = {"index":"Metabolites"})
        
        #Create information sheet content      
        pcaVIPscores_info_sheet = pd.DataFrame({'Column': ['Metabolite',  
                                     'PC1 VIP score'],
                          'Explanation': ['The metabolites with the top 50 Variable Importance Point (VIP) scores', 
                                          'VIP score for each metabolite from the PC1 PCA axis']})
        
        writer = pd.ExcelWriter(f"EdinOmics_{project_no}_pca_vip_scores.xlsx", 
                                engine = 'xlsxwriter')
        
        pcaVIPscores_info_sheet.to_excel(writer, sheet_name = 'ReadMe', index = False)
        pca_top_50_features.to_excel(writer, sheet_name = 'PCAVIPScores', index = False)
        
        writer.close()
 
#Download PLS-DA scores file as .xlsx
#Last updated: 04/08/2025 (Jessica O'Loughlin)
def plsda_scores_download(n_clicks, n_clicks_inTab, data, project_no):
    if n_clicks or n_clicks_inTab is None:
        raise PreventUpdate
    else:
        dff = pd.DataFrame(data)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        str_variables = set(dff.select_dtypes("object" or "str").columns)
        

        #Automatically generate list of metabolites
        #Remove the str_variables to get metabolites only
        metabolite_list = [metabolite for metabolite in 
                           list(dff.columns) if metabolite not in list(str_variables)]
        
        #Add these numbers into the data
        plsda_df = dff.copy()
        
        #Get number of data rows (excluding row containing metabolite names)
        comp_num = len(plsda_df)-1
        
        #Get cls dataframe
        # cls_data = pd.DataFrame()
        cls_data = plsda_df[['Label']]

        # Convert categorical data to numerical data using cat.codes
        cls_data['Label'] = cls_data['Label'].astype('category')
        cls_data['x_codes'] = cls_data['Label'].cat.codes
        cls_data['x_codes'] = cls_data['x_codes']+1
        
        #R's base scale() function translated into Python
        def scale_default(x, center=True, scale=True):
            x = np.asarray(x)  # Make sure x is a NumPy array
            if x.ndim == 1:
                x = x.reshape(-1, 1)  # Work with 2D array for consistency
            
            nc = x.shape[1]

            # Centering the data
            if isinstance(center, bool):
                if center:
                    center = np.nanmean(x, axis=0)  # Compute mean considering NaN
                    x = x - center
            elif isinstance(center, (list, np.ndarray)):
                if len(center) != nc:
                    raise ValueError("length of 'center' must equal the number of columns of 'x'")
                x = x - center
            else:
                raise ValueError("center must be either a boolean or a numeric array")

            # Scaling the data
            if isinstance(scale, bool):
                if scale:
                    scale = np.sqrt(np.nansum(x**2, axis=0) / np.maximum(1, np.sum(~np.isnan(x), axis=0) - 1))
                    x = x / scale
            elif isinstance(scale, (list, np.ndarray)):
                if len(scale) != nc:
                    raise ValueError("length of 'scale' must equal the number of columns of 'x'")
                x = x / scale
            else:
                raise ValueError("scale must be either a boolean or a numeric array")

            return x

        cls_scaled = scale_default(cls_data['x_codes'], center = True, scale = True)
        
        #Remove the string variables
        plsda_df = plsda_df.drop(str_variables, axis = 1)
        
        #Fit the PLS-DA regression model
        pls = PLSRegression(n_components=comp_num, scale=False) # (1)
        pls.fit(plsda_df, cls_scaled) # (2)
          
        #Create a data frame with the PLS-DA score results
        scores = pd.DataFrame(pls.x_scores_)
        scores = scores.rename(columns = {0:"Component 1", 1:"Component 2",
                                          2:"Component 3"})
        scores = scores[["Component 1", "Component 2", "Component 3"]]
        
        #Remove metabolites (only keep sample labels)
        dff = dff.drop(metabolite_list, axis = 1)
        
        #Add the sample and metabolite information from the main data frame
        scores = pd.concat([dff.reset_index(drop = True), 
                            scores], 
                           axis = 1)
        
        #Create information sheet content      
        plsdaScores_info_sheet = pd.DataFrame({'Column': ['Sample', 
                                     'Label', 
                                     'Component 1',
                                     'Component 2',
                                     'Component 3'],
                          'Explanation': ['Each individual sample name', 
                                          'The group each sample belongs to', 
                                          'Position of the sample datapoint along the Component 1 axis', 
                                          'Position of the sample datapoint along the Component 2 axis', 
                                          'Position of the sample datapoint along the Component 3 axis']})
        
        writer = pd.ExcelWriter(f"EdinOmics_{project_no}_pls-da_scores_results.xlsx", 
                                engine = 'xlsxwriter')
        
        plsdaScores_info_sheet.to_excel(writer, sheet_name = 'ReadMe', index = False)
        scores.to_excel(writer, sheet_name = 'PLSDAScores', index = False)
        
        writer.close()

#Download PLS-DA loadings file as .xlxs
#Last updated: 04/08/2025 (Jessica O'Loughlin)        
def plsda_loadings_download(n_clicks, n_clicks_inTab, data, project_no):
    if n_clicks or n_clicks_inTab is None:
        raise PreventUpdate
    else:
        dff = pd.DataFrame(data)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        str_variables = set(dff.select_dtypes("object" or "str").columns)
        

        #Automatically generate list of metabolites
        #Remove the str_variables to get metabolites only
        metabolite_list = [metabolite for metabolite in 
                           list(dff.columns) if metabolite not in list(str_variables)]
        
        #Add these numbers into the data
        plsda_df = dff.copy()
        
        #Get number of data rows (excluding row containing metabolite names)
        comp_num = len(plsda_df)-1
        
        #Get cls dataframe
        cls_data = plsda_df[['Label']]

        # Convert categorical data to numerical data using cat.codes
        cls_data['Label'] = cls_data['Label'].astype('category')
        cls_data['x_codes'] = cls_data['Label'].cat.codes
        cls_data['x_codes'] = cls_data['x_codes']+1
        
        #R's base scale() function translated into Python
        def scale_default(x, center=True, scale=True):
            x = np.asarray(x)  # Make sure x is a NumPy array
            if x.ndim == 1:
                x = x.reshape(-1, 1)  # Work with 2D array for consistency
            
            nc = x.shape[1]

            # Centering the data
            if isinstance(center, bool):
                if center:
                    center = np.nanmean(x, axis=0)  # Compute mean considering NaN
                    x = x - center
            elif isinstance(center, (list, np.ndarray)):
                if len(center) != nc:
                    raise ValueError("length of 'center' must equal the number of columns of 'x'")
                x = x - center
            else:
                raise ValueError("center must be either a boolean or a numeric array")

            # Scaling the data
            if isinstance(scale, bool):
                if scale:
                    scale = np.sqrt(np.nansum(x**2, axis=0) / np.maximum(1, np.sum(~np.isnan(x), axis=0) - 1))
                    x = x / scale
            elif isinstance(scale, (list, np.ndarray)):
                if len(scale) != nc:
                    raise ValueError("length of 'scale' must equal the number of columns of 'x'")
                x = x / scale
            else:
                raise ValueError("scale must be either a boolean or a numeric array")

            return x

        cls_scaled = scale_default(cls_data['x_codes'], center = True, scale = True)
        
        #Remove the string variables
        plsda_df = plsda_df.drop(str_variables, axis = 1)
        
        #Fit the PLS-DA regression model
        pls = PLSRegression(n_components=comp_num, scale=False) # (1)
        pls.fit(plsda_df, cls_scaled) # (2)
        
        loadings = pd.DataFrame(pls.x_weights_)
        loadings = loadings.rename(columns = {0:"Loadings 1", 1:"Loadings 2",
                                             2:"Loadings 3"})
        #Add the metabolite list to the loadings data
        loadings["Metabolite"] = metabolite_list
        #Reorder columns
        loadings = loadings.loc[:,["Metabolite", "Loadings 1", "Loadings 2", 
                                   "Loadings 3"]]
        
        #Create information sheet content      
        plsdaLoadings_info_sheet = pd.DataFrame({'Column': ['Metabolite',  
                                     'Loadings 1',
                                     'Loadings 2',
                                     'Loadings 3'],
                          'Explanation': ['Metabolites present in the user-selected data from the interactive report', 
                                          'Position of the metabolite datapoint along the Loadings 1 axis', 
                                          'Position of the metabolite datapoint along the Loadings 2 axis', 
                                          'Position of the metabolite datapoint along the Loadings 3 axis']})
        
        writer = pd.ExcelWriter(f"EdinOmics_{project_no}_pls-da_loadings_results.xlsx", 
                                engine = 'xlsxwriter')
        
        plsdaLoadings_info_sheet.to_excel(writer, sheet_name = 'ReadMe', index = False)
        loadings.to_excel(writer, sheet_name = 'PLSDALoadings', index = False)
        
        writer.close()

#Download PLS-DA VIP scores file as .xlsx
#Last updated: 04/08/2025 (Jessica O'Loughlin)        
def plsda_vip_scores_download(n_clicks, n_clicks_inTab, data, project_no):
    if n_clicks or n_clicks_inTab is None:
        raise PreventUpdate
    else:
        dff = pd.DataFrame(data)
        
        #Define the variables (columns) which contain characters/strings
        #These sometimes need to be removed for downstream calculations
        str_variables = set(dff.select_dtypes("object" or "str").columns)
        
        #Add these numbers into the data
        plsda_df = dff.copy()
        
        #Get number of data rows (excluding row containing metabolite names)
        comp_num = len(plsda_df)-1
        
        #Get cls dataframe
        # cls_data = pd.DataFrame()
        cls_data = plsda_df[['Label']]

        # Convert categorical data to numerical data using cat.codes
        cls_data['Label'] = cls_data['Label'].astype('category')
        cls_data['x_codes'] = cls_data['Label'].cat.codes
        cls_data['x_codes'] = cls_data['x_codes']+1
        
        #R's base scale() function translated into Python
        def scale_default(x, center=True, scale=True):
            x = np.asarray(x)  # Make sure x is a NumPy array
            if x.ndim == 1:
                x = x.reshape(-1, 1)  # Work with 2D array for consistency
            
            nc = x.shape[1]

            # Centering the data
            if isinstance(center, bool):
                if center:
                    center = np.nanmean(x, axis=0)  # Compute mean considering NaN
                    x = x - center
            elif isinstance(center, (list, np.ndarray)):
                if len(center) != nc:
                    raise ValueError("length of 'center' must equal the number of columns of 'x'")
                x = x - center
            else:
                raise ValueError("center must be either a boolean or a numeric array")

            # Scaling the data
            if isinstance(scale, bool):
                if scale:
                    scale = np.sqrt(np.nansum(x**2, axis=0) / np.maximum(1, np.sum(~np.isnan(x), axis=0) - 1))
                    x = x / scale
            elif isinstance(scale, (list, np.ndarray)):
                if len(scale) != nc:
                    raise ValueError("length of 'scale' must equal the number of columns of 'x'")
                x = x / scale
            else:
                raise ValueError("scale must be either a boolean or a numeric array")

            return x

        cls_scaled = scale_default(cls_data['x_codes'], center = True, scale = True)
        
        #Remove the string variables
        plsda_df = plsda_df.drop(str_variables, axis = 1)
        
        #Fit the PLS-DA regression model
        pls = PLSRegression(n_components=comp_num, scale=False) # (1)
        pls.fit(plsda_df, cls_scaled) # (2)

        ##VIP score calculations
        # Change pcs components ndarray to a dataframe
        importance_df = pd.DataFrame(pls.x_rotations_)
        importance_df = importance_df.transpose()
        
        # Assign columns
        importance_df.columns  = plsda_df.columns
        #importance_df = importance_df.drop("num_cat", axis = 1)
        # Change to absolute values
        importance_df =importance_df.apply(np.abs)
        # Transpose
        importance_df=importance_df.transpose()
        # Change column names again
        # First get number of pcs
        num_pcs = importance_df.shape[1]
        ## Generate the new column names
        new_columns = [f'PLSDA{i} VIP score' for i in range(1, num_pcs + 1)]
        ## Now rename
        importance_df.columns = new_columns  
        #Multiply VIP score values by 10
        importance_df = importance_df.apply(lambda x: x*10)
        #PLSDA axis 1 top 50 important features
        pls1_top_50_features = importance_df['PLSDA1 VIP score'].sort_values(ascending = False)[:50]
        pls1_top_50_features = pls1_top_50_features.reset_index()
        pls1_top_50_features = pls1_top_50_features.rename(columns = {"index":"Metabolites"})
        
        #Create information sheet content      
        plsdaVIPscores_info_sheet = pd.DataFrame({'Column': ['Metabolite',  
                                     'PLSDA1 VIP score'],
                          'Explanation': ['The metabolites with the top 50 Variable Importance of Projection (VIP) scores', 
                                          'VIP score for each metabolite from the Component 1 PLS-DA axis']})
        
        writer = pd.ExcelWriter(f"EdinOmics_{project_no}_pls-da_vip_scores.xlsx", 
                                engine = 'xlsxwriter')
        
        plsdaVIPscores_info_sheet.to_excel(writer, sheet_name = 'ReadMe', index = False)
        pls1_top_50_features.to_excel(writer, sheet_name = 'PLSDAVIPScores', index = False)
        
        writer.close()
        