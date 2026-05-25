
<p float="center">
  <img alt="GitHubImage" src="https://github.com/user-attachments/assets/5f702018-d773-4fee-ba77-d7810235519a" width="1000" /> 
</p>

# A Python Dash App and cPanel workflow to automate metabolomics data analyses and visualisation
Your untargeted metabolomics analysis results are shared as an interactive report. This repository publicly provides the underlying algorithms behind the statistical analyses performed on data and how they are visualised. 

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
Once logged in, you should see a list of reports for experiments performed by your group. Typically, there are two types of reports: Methods pages containing experimental details and Results where you can view your metabolomics data. 

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

# Structure and details of files required to deploy our Dash App reports
These can be viewed and downloaded from the `ExampleHomeDirectoryForApp` folder

```
ExampleHomeDirectoryForApp:
├── AccessDetails.txt                         #Store username and password details for each user account
├── app.py                                    #Startup file and entry point for Dash Application
├── ExampleData-MetabolomicsResults.csv       #Example of entire metabolomics dataset (tidied up from Mass Profiler annotated output)
├── ExampleData-SamplesAndLabels.csv          #For each dataset, have a file with only the sample names and group labels
├── passenger_wsgi.py                         #Web Server Gateway Interface: Requirement only for deployment via cPanel 
├── ReportDescriptiveText.py                  #Read by methods scripts as a reference to commonly cited protocol steps
├── ReportFunctions.py                        #Read by results scripts to access functions to load, normalise, process, and download a user's data
├── requirements.txt                          #Modules and versions required in your Python environment to run this app
├── assets                                    #Images and external styling files read by app.py
│   ├── EdinOmics_Logo_Transparent.png
│   ├── favicon.ico
│   ├── style.css
│   ├── typography.css
│   └── university-of-edinburgh-logo.png
├── pages
│   ├── ExampleUser_MethodPage.py             #Typical layout of a methods report
│   ├── ExampleUser_ResultsPage.py            #Typical layout of a results report
│   ├── ExampleUser_UserHomePage.py           #Central home page for each user, where users are initially directed to upon logging in to access their reports
│   ├── login.py                              #Home directory in app.py. Initially prompts user to log in to access their data
│   └── logout.py                             #Ensure successful logging out of a profile
└── README_DeployAppInfo.md
```

# Steps to set up and initially deploy this Python Dash App via cPanel
### Note: As some files are overwritten during this process, ensure that you have copies of app.py and passenger_wsgi.py in separate directories before you start these steps. 

1) Set up the home directory for your Dash App within `public_html` of cPanel
2) Nagivate to the "Setup Python App" option within cPanel's "Software" tab
3) Select "CREATE APPLICATION"
4) Set up the app environment with the following settings:
   * Python version = 3.9.19
   * Application root = public_html/ExampleHomeDirectoryForApp
   * Application URL = {leave blank}
   * Startup file = app.py
   * Entry point = app
   * Passenger log file = /home/{user_home_directory}/logs/passenger.log
5) Select "CREATE"
6) Perform initial checks
   * Select "OPEN" to view your app
   * Should have a printed output `It works!` alongside the Python version
   * cPanel automatically creates additional files in our directory and overwrites app.py and passenger_wsgi.py
7) Select "STOP APP"
8) Return to the cPanel File Manager page and refresh it
9) Re-upload your app.py file to overwrite the app.py added in by cPanel
    * View app.py to ensure that your one has successfully overwritten cPanel's app.py
10) Return to the Python app tab
11) In the "Configuration files" section type `requirements.txt` and press the "Enter" key on your keyboard
    * This has uploaded the requirements.txt file
12) Select "Run Pip Install", which will drop down `requirements.txt` as an option to select
13) Select `requirements.txt` and wait until the modules have been successfully installed
    * Sometimes, specifying the module versions in `requirements.txt` can cause error messages to occur at this stage but the modules have still been installed successfully
    * You can navigate to the environment's terminal and use `pip freeze` to check that all the required modules have been installed before progressing
14)  Select "START APP"
15)  Return to the cPanel File Manager page and refresh it
16)  Upload your `passenger_wsgi.py` to overwrite the one put in by cPanel
17)  Return to your Python app tab
18)  Select "RESTART" to restart the app with these changes
19)  Select "OPEN"
     * You should now be able to view your app's home page
     * Interact with the app to make sure that it works properly
20) For any problems, see the passenger.log (error log) in the logs folder in the cPanel File Manager to help narrow down the problem
21) See the Troubleshooting Guidance at the bottom of this page to possible fixes to common problems
       
# Steps to update the Dash App to upload additional users/reports

1) Ensure that your metabolomics data files are in the correct format
   * Main metabolomics results (`mainDataset`)
     * This Dash App is designed to read metabolomics data in CSV file format with the "Samples in columns (unpaired)" structure that MetaboAnalyst uses, with structure and **exact row names** as shown below:
     
| Sample                                          | A Ext 1  | A Ext 2  | A Ext 3  | A Int 1  | A Int 2  | A Int 3  |
|-------------------------------------------------|----------|----------|----------|----------|----------|----------|
| Label                                           | A Ext    | A Ext    | A Ext    | A Int    | A Int    | A Int    |
| (S)-Adenosyl-L-methionine                       | 0.001    | 0.001    | 166899   | 0.001    | 178408.2 | 0.001    |
| (S)-Carboxymethyl-L-cysteine                    | 303374.1 | 215336.9 | 266310.2 | 0.001    | 0.001    | 0.001    |
| (S)-Hexyl-glutathione                           | 200957.2 | 178056   | 165733.8 | 0.001    | 55653.89 | 65993.74 |
| (S)-Taurocholic Acid                            | 1.34E+07 | 1.19E+07 | 1.20E+07 | 1.24E+07 | 1.19E+07 | 1.26E+07 |
| (S)-Taurodeoxycholic Acid                       | 0.001    | 0.001    | 0.001    | 0.001    | 0.001    | 0.001    |
| 1,2-Didecanoyl-sn-glycero-3-phosphoethanolamine | 0.001    | 0.001    | 0.001    | 0.001    | 0.001    | 0.001    |


   * File containing sample names and group labels (`samplesLabels`)
     * To reduce the memory and performance impact that very large metabolomics datasets can have on the Dash app's performance, the sample names and group labels are put into this separate CSV file as well to allow the user to initially select their desired samples for analysis before the entire metabolomics dataset is loaded (and potentially quickly subset to only the user's desired samples to analyse)
     
| Sample  | Label |
|---------|-------|
| A Ext 1 | A Ext |
| A Ext 2 | A Ext |
| A Ext 3 | A Ext |
| A Int 1 | A Int |
| A Int 2 | A Int |
| A Int 3 | A Int |

     
1) It is recommended that you duplicate existing equivalent of the `ExampleUser_MethodPage.py`, `ExampleUser_ResultsPage.py` and, **if adding a new user account**, `ExampleUser_UserHomePage.py` files in the `pages` subdirectory and edit these as outlined below:
   
   a) `ExampleUser_MethodPage.py`
     * The link for `accountIndexPage` should match the url in the path of `ExampleUser_UserHomePage.py` (and start with "/")
     * `page_name` is the name of the page to be displayed to the user. This should be added within the list contained in `if page["name"].startswith((...))` in the report's respective `ExampleUser_UserHomePage.py`
     * `path` should have its own unique url (starting with "/")
     * The `order` should be changed to reflect which position you would like this report to be viewed in the user's home page (where the first page is "0")
     * Update any general methods information in the rest of the script to align to those used for this user
       
   b) `ExampleUser_ResultsPage.py`
     * The link for `accountIndexPage` should match the url in the path of `ExampleUser_UserHomePage.py`
     * `page_name` is the name of the page to be displayed to the user. This should be added within the list contained in `if page["name"].startswith((...))` in the report's respective `ExampleUser_UserHomePage.py`
     * `mainDataset` is set to the file name (containing .csv extension) of the main metabolomics results file 
     * `samplesLabels` is set to the file name (containing .csv extension) containing the Sample names and group labels for these metabolomics results
     * `path` should have its own unique url (starting with "/")
     * The `order` should be changed to reflect which position you would like this report to be viewed in the user's home page (where the first page is "0")
     * `project_no` should be changed to the desired project number for this project. This is added as a prefix to the names of files that the users download
     * Use a replace tool in whichever text editor you are using so that the IDs of each element in the report have a suffix unique to this report
       * Otherwise, the presence of duplicate IDs in callbacks (i.e. those present in other pages) will cause the Dash App to crash
       
   c) `ExampleUser_UserHomePage.py` (and also updating the existing `app.py`)
     * Update the existing `app.py`
       * In the `login_button_click()` function at the bottom of the script, copy an `elif` statement and change the `current_user.get_id()` and `href`
     * `ExampleUser_UserHomePage.py`
       * `name` should have the User's name
       * `path` should match `accountIndexPage` in the `ExampleUser_MethodPage.py` and `ExampleUser_ResultsPage.py` scripts **and** the `href` for that user account in the `login_button_click()` function of `app.py`
       * The first `html.H2` within the layout's `html.Div([])` should also have the name of the User specified
       * The list contained in `if page["name"].startswith((...))` should have all the `name` for each page to be included in this user's home page to potentially select (including previously uploaded pages if you still want these to be available)
      
2) It is recommended that locally deploy these files first to test them at this point to ensure that A) they work as expected and B) do not contain errors with may crash the web hosted version of the app
3) Log into cPanel
4) Within the app's root directory, add:
   * The CSV data files and (only if a new user profile is being added) the updated version of `app.py` into the app's home directory
   * `ExampleUser_MethodPage.py`, `ExampleUser_ResultsPage.py`, and `ExampleUser_UserHomePage.py` into the `pages` subdirectory
5) Navigate to cPanel's "Setup Python App" option in the "Software" tab
6) Reset the currently running instance of the app to incorporate the files and changes you have just added
7) Check the app to ensure that the newly added reports and accounts are accessible and work as expected
8) For any problems, see the passenger.log (error log) in the logs folder in the cPanel File Manager to help narrow down the problem
9) See the Troubleshooting Guidance at the bottom of this page to possible fixes to common problems

# Troubleshooting Guidance
### Cannot deploy first instance of Python Dash app
Occassionally, files running in the background from previous instances of the app can cause conflicts (even if they are seemingly removed). I have personally found that contacting your hosting provider and requesting to reset your cPanel account to the last backed-up point where it was working can fix this. **Ensure that you save your data onto your PC before the reset**.

### Pages are not being displayed (and there is no error message)
This is usually due to paths not being correctly declared or linked together
* Check `href` links
* Temporarily paste the following code to print out the page details in passenger.log to check if the pages have the expected details registered

```
total_no_pages = 0
for page in dash.page_registry.values():
    print(page["module"])
    print(page["name"])
    print(page["path"])
    print(page["relative_path"])
    total_no_pages += 1
    print("---------")
print("total_no_pages in app.py:", total_no_pages)
```
