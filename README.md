# A Python Dash App and cPanel workflow to automate metabolomics data analyses and visualisation
For many customers who provide samples for untargeted metabolomics analyses, we may send your data back to you as an interactive report. This repository publicly provides the underlying algorithms behind the statistical analyses performed on data and how they are visualised. 

# Using the interactive reports
For details on how to access and navigate your interactive report to make the most out of all its features, please read this section. 

## Accessing your report
### Login to your report
At the login page, which can be accessed [here](https://edinomics.report.bio.ed.ac.uk/), enter your group's username and password details provided to you by EdinOmics. 

If you are unable to login:
1) Make sure that Caps Lock is switched off
2) You have not added any empty spaces at the beginning or end of the username/password when typing it out

If issues persist, contact edinomics@ed.ac.uk for assistance. 

### Select your desired report
Once logged in, you should see a list of reports for samples sent in to your group. Typically, there are two types of reports: Methods pages containing experimental details and Results where you can view your metabolomics data. 

## View your metabolomics results
To access your results, you simply need to select the samples groups or individual samples you wish to analyse and then select "Update form with data selection". 

### Data normalisation
Raw metabolomics data is usually heavily left-skewed, where there are many metabolites present in relatively low intensities and a few metabolites at higher intensities. Whilst this is somewhat expected in most biological contexts it is not ideal for statistical analyses. Therefore, the data you select is first *normalised* so that the distribution of intensities follow a more Gaussian/normal distribution, which is then used in *most* statistical calculations. These distributions can be visualised in the Raw Data and Normalised Data tabs in your report. 

### Graphical and spreadsheet outputs
Once your selected data has been normalised and statistical calculations performed, your results can now be viewed. 

#### Graphs 
If using a computer/laptop, hovering over any graph with your cursor will display a number of options to allow you to zoom in/select regions of interest to view as well as download your graphs as PNG files. If using a touch screen device, these same options should display if you press the centre of your graph once. 

#### Spreadsheets
All data can also be downloaded as Excel worksheets. These are ideal if you want to save your data offline, manually inspect your data, or make graphs to your own aesthetic or publication requirements. To get these, select the Download Data options either in the tab for each respective statistical analysis type or accesss them all in the "Download Data" tab. 

# Deploy your own reports/access code used in these reports
Further details about the background code used by these reports as well as guidance about deploying these apps, please see the `AppCode` directory of this repository. 
